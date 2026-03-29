"""
aether_ai — News Summarizer Service

Accepts raw text or a URL, returns:
  - abstractive summary (2-3 sentences via LLM)
  - key takeaways (5 bullet points)
  - category detection (markets/startup/policy/macro/tech)
  - estimated read time
"""
import re
import math
import concurrent.futures
import json
from pydantic import BaseModel, ValidationError
from typing import Any, Dict, List, Optional
from app.core.config import get_llm_client
from app.services.rss_service import fetch_article_text
from app.services.story_arc_service import _get_spacy


CATEGORY_KEYWORDS = {
    "markets": ["sensex", "nifty", "bse", "nse", "stock", "share", "equity", "ipo", "sebi", "market"],
    "startup": ["startup", "founder", "funding", "series", "unicorn", "venture", "seed", "pitch", "valuation"],
    "policy": ["government", "ministry", "rbi", "budget", "policy", "regulation", "law", "parliament", "gazette"],
    "macro": ["gdp", "inflation", "cpi", "interest rate", "fiscal", "monetary", "economy", "recession", "growth"],
    "tech": ["ai", "software", "app", "platform", "saas", "tech", "digital", "cloud", "data", "cyber"],
}


def _detect_category(text: str) -> str:
    lower = text.lower()
    scores = {cat: sum(lower.count(kw) for kw in kws) for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def _estimate_read_time(text: str) -> int:
    """Average reading speed ~200 wpm."""
    words = len(text.split())
    return max(1, math.ceil(words / 200))


def _extractive_fallback(text: str, n_sentences: int = 5) -> List[str]:
    """
    Simple extractive summarizer — scores sentences by keyword frequency.
    Used when LLM is unavailable.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if len(sentences) <= n_sentences:
        return sentences

    # Word frequency scoring
    words = re.findall(r"\b\w+\b", text.lower())
    freq: Dict[str, int] = {}
    for w in words:
        if len(w) > 3:
            freq[w] = freq.get(w, 0) + 1

    scored = []
    for s in sentences:
        score = sum(freq.get(w.lower(), 0) for w in re.findall(r"\b\w+\b", s))
        scored.append((score, s))

    scored.sort(reverse=True)
    top = [s for _, s in scored[:n_sentences]]
    return top


class SummarizerSchema(BaseModel):
    summary: str
    key_takeaways: List[str]
    contextual_impact: str


def _chunk_text(text: str, chunk_size: int = 2500) -> List[str]:
    """Break long articles into sentences bounded to chunk_size to maintain semantics."""
    nlp = _get_spacy()
    if not nlp:
        # Fast fallback
        sents = text.split(". ")
    else:
        doc = nlp(text)
        sents = [s.text for s in doc.sents]
        
    chunks = []
    current_chunk = []
    current_len = 0
    for s in sents:
        if current_len + len(s) > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [s]
            current_len = len(s)
        else:
            current_chunk.append(s)
            current_len += len(s)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks


def _summarize_chunk(chunk: str) -> str:
    """Map phase: Extract raw bullet points from a single chunk using local LLM."""
    prompt = f"""Extract bullet points of all critical facts, numbers, names, dates, and actions from this text segment.
Do not hallucinate or add outside knowledge. Extract verbatim facts only.

TEXT:
{chunk}"""
    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


def _consolidate_summaries(facts: List[str]) -> Dict[str, Any]:
    """Reduce phase: Combine all chunk-facts into a flawless, zero-hallucination structured JSON."""
    context = "\n---\n".join(f"CHUNK {i+1} FACTS:\n{f}" for i, f in enumerate(facts) if f.strip())
    prompt = f"""You are an expert business news editor. Synthesize the following chunked facts extracted from a long article into a cohesive, high-quality news summary.
DO NOT hallucinate information not explicitly present in these facts. Provide specific numbers and names where available.

FACTS:
{context}

Respond in this EXACT JSON structure ONLY (no markdown fences):
{{
  "summary": "Crisp 3-sentence narrative summary strictly connecting the key facts.",
  "key_takeaways": [
    "Fact 1 starting with strong verb", "Fact 2", "Fact 3", "Fact 4", "Fact 5"
  ],
  "contextual_impact": "1-2 sentence analysis on why this matters to the broader market/industry, derived strictly from the facts."
}}"""
    
    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content.strip()
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        clean = json_match.group(0) if json_match else raw
        parsed = json.loads(clean)
        return SummarizerSchema(**parsed).model_dump()
    except Exception as e:
        print(f"Map-Reduce Consolidation Error: {e}")
        return {}


def summarize(text: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Main summarization pipeline.
    Priority: url → scrape text; text → use directly.
    Returns summary dict.
    """
    # ── 1. Resolve input ──────────────────────────────────────────────────────
    if url:
        raw_text = fetch_article_text(url)
        if not raw_text:
            return {"error": "Could not fetch article from URL. Try pasting the text directly."}
    elif text:
        raw_text = text.strip()
    else:
        return {"error": "Provide either text or url."}

    if len(raw_text) < 100:
        return {"error": "Text too short to summarize."}

    # ── 2. Metadata (no LLM needed) ───────────────────────────────────────────
    category = _detect_category(raw_text)
    read_time = _estimate_read_time(raw_text)

    # ── 3. Map-Reduce Summarization Pipeline ──────────────────────────────────
    chunks = _chunk_text(raw_text, chunk_size=3000)
    
    # ThreadPool for parallel Map Phase execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        chunk_facts = list(executor.map(_summarize_chunk, chunks))

    # Reduce Phase Execution
    final_output = _consolidate_summaries(chunk_facts)

    if final_output:
        summary = final_output.get("summary", "")
        takeaways = final_output.get("key_takeaways", [])
        impact = final_output.get("contextual_impact", "")
    else:
        # Fallbacks for extreme errors
        fallback_sents = _extractive_fallback(raw_text, n_sentences=3)
        summary = " ".join(fallback_sents[:2])
        takeaways = _extractive_fallback(raw_text, n_sentences=5)
        impact = "System offline. Contextual analysis unavailable."

    return {
        "summary": summary,
        "key_takeaways": takeaways[:5],
        "contextual_impact": impact,
        "category": category,
        "read_time_min": read_time,
        "char_count": len(raw_text),
        "chunk_count": len(chunks)
    }
