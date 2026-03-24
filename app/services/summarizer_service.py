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
from typing import Any, Dict, List, Optional
from app.core.config import get_llm_client
from app.services.rss_service import fetch_article_text


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

    # ── 3. LLM summarization ──────────────────────────────────────────────────
    # Truncate to ~3000 chars for LLM context efficiency
    truncated = raw_text[:3500]

    prompt = f"""You are an expert business news editor. Summarize the following article concisely for a busy professional.

ARTICLE:
{truncated}

Respond in this exact JSON format (no markdown fences):
{{
  "summary": "A crisp 2-3 sentence abstractive summary covering the who, what, and why.",
  "key_takeaways": [
    "Takeaway 1 — specific and actionable",
    "Takeaway 2 — specific and actionable",
    "Takeaway 3 — specific and actionable",
    "Takeaway 4 — specific and actionable",
    "Takeaway 5 — specific and actionable"
  ]
}}

Rules:
- Summary must be in plain English, no jargon
- Each takeaway must start with a strong verb or data point
- Return ONLY the JSON, no extra text"""

    client, model = get_llm_client()
    summary = ""
    takeaways: List[str] = []

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        import json
        parsed = json.loads(raw)
        summary = parsed.get("summary", "")
        takeaways = parsed.get("key_takeaways", [])
    except Exception:
        # Extractive fallback — still useful, just less polished
        fallback_sents = _extractive_fallback(raw_text, n_sentences=3)
        summary = " ".join(fallback_sents[:2])
        takeaways = _extractive_fallback(raw_text, n_sentences=5)

    return {
        "summary": summary,
        "key_takeaways": takeaways[:5],
        "category": category,
        "read_time_min": read_time,
        "char_count": len(raw_text),
    }
