"""
aether_ai — Vernacular Business News Engine

Translates English business news into Hindi, Tamil, Telugu, Bengali with:
  - Base translation via local Ollama indicating high literal translation
  - LLM-powered naturalness post-processing (business terminology adaptation via chunking map-reduce)
  - Pre-translation entity protection (RBI, SEBI, etc.)
  - Local cultural context note explaining financial terms to local readers
  - Business terminology glossary extraction
"""
import re
import json
import concurrent.futures
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel
from app.core.config import get_llm_client
from app.services.story_arc_service import _get_spacy

SUPPORTED_LANGUAGES = {
    "hi": {"name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇮🇳"},
}

class GlossaryTerm(BaseModel):
    term: str
    translation: str
    explanation: str

class VernacularSchema(BaseModel):
    improved_translation: str
    local_context_note: str
    terminology_glossary: List[GlossaryTerm]

# ── 1. Entity Protection ──────────────────────────────────────────────────────
def _protect_entities(text: str) -> Tuple[str, Dict[str, str]]:
    """Find key financial acronyms and replace them with static mapping tags to prevent malformed translation."""
    mapping = {}
    protected_text = text
    acronyms = ["RBI", "SEBI", "GDP", "IPO", "FDI", "FPI", "NSE", "BSE", "MSME", "GST", "CAGR", "EBITDA"]
    words = ["Sensex", "Nifty", "Repo Rate", "Reserve Bank"]
    
    counter = 1
    for term in acronyms + words:
        # Regex to match whole words safely
        pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
        
        # We process matches one by one to give each a unique tag
        for match in pattern.finditer(protected_text):
            tag = f"__ENT_{counter}__"
            mapping[tag] = match.group(0)
            protected_text = protected_text.replace(match.group(0), tag, 1)
            counter += 1
            
    return protected_text, mapping

def _restore_entities(text: str, mapping: Dict[str, str]) -> str:
    """Restore the mapping tags back to original text."""
    restored = text
    for tag, original in mapping.items():
        restored = restored.replace(tag, original)
    return restored

# ── 2. Semantic Chunking ──────────────────────────────────────────────────────
def _chunk_text_vernacular(text: str, max_chars: int = 1200) -> List[str]:
    """Segment text by SpaCy sentence boundary to avoid slicing words mid-sentence."""
    nlp = _get_spacy()
    if not nlp:
        # fallback chunking
        return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_len = 0
    for s in doc.sents:
        if current_len + len(s.text) > max_chars and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [s.text]
            current_len = len(s.text)
        else:
            current_chunk.append(s.text)
            current_len += len(s.text)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# ── 3. Base Translation Pass ──────────────────────────────────────────────────
def _base_translate_chunk(chunk: str, target_lang: str) -> str:
    """Literal base translation using Ollama map pass."""
    prompt = f"""You are a professional literal translator. Translate the following English text to {target_lang}. 
DO NOT translate or alter any placeholder tags formatted like __ENT_1__. Preserve them exactly verbatim.
Output ONLY the translated text without markdown or conversational prefixes.

TEXT:
{chunk}"""
    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return chunk

# ── 4. Refinement Pass ────────────────────────────────────────────────────────
def _refine_translation(base_translated: str, mapping: Dict[str, str], target_lang_name: str, model_name: str) -> Dict[str, Any]:
    """LLM Post-processor: restore tags, smooth grammar, create JSON outputs."""
    # Restore entities before sending to LLM context
    restored = _restore_entities(base_translated, mapping)
    
    prompt = f"""You are an elite bilingual business news editor for {target_lang_name} audiences in India.
    
BASE TRANSLATION (Rough literal format):
{restored[:8000]}

Your task is to:
1. Refine the rough base translation into highly fluent, professional journalistic {target_lang_name}. It must read naturally for financial audiences.
2. Keep specific financial entities (e.g. RBI, SEBI, GDP, Nifty, Sensex) intact.
3. Formulate a short "local_context_note" in English explaining why this news matters to local readers.
4. Extract a terminology glossary of 3-5 financial terms used.

Respond STRICTLY in this JSON format ONLY (No markdown fences):
{{
  "improved_translation": "The entire refined fluent text strictly in {target_lang_name} script.",
  "local_context_note": "2-sentence cultural or economic context note in English.",
  "terminology_glossary": [
    {{"term": "English Term", "translation": "{target_lang_name} equivalent", "explanation": "English definition"}}
  ]
}}"""

    client, _ = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        raw = resp.choices[0].message.content.strip()
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        clean = json_match.group(0) if json_match else raw
        parsed = json.loads(clean)
        # Validate deterministic shapes via Pydantic
        validated = VernacularSchema(**parsed)
        return validated.model_dump()
    except Exception as e:
        print(f"Vernacular Refinement Error: {str(e)}")
        return {
            "improved_translation": restored,
            "local_context_note": "Refinement unavailable.",
            "terminology_glossary": []
        }

# ── 5. Main Orchestrator ──────────────────────────────────────────────────────
def translate_text(text: str, target_lang: str, model_name: str = "llama3.1:8b") -> Dict[str, Any]:
    """
    Full vernacular translation pipeline using a dual-pass Ollama architecture.
    """
    if target_lang not in SUPPORTED_LANGUAGES:
        return {"error": f"Unsupported language '{target_lang}'. Choose: hi, ta, te, bn"}

    if not text or len(text.strip()) < 10:
        return {"error": "Text too short to translate."}

    lang_info = SUPPORTED_LANGUAGES[target_lang]
    lang_name = lang_info["name"]
    
    # 1. Protect Entities
    protected_text, mapping = _protect_entities(text.strip())
    
    # 2. Chunk English Content safely
    chunks = _chunk_text_vernacular(protected_text)
    
    # 3. Base Translation Pass (Map)
    base_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        base_results = list(executor.map(lambda c: _base_translate_chunk(c, lang_name), chunks))
    
    full_base_translated = " ".join(base_results)
    
    # 4. Refinement Pass (Reduce)
    llm_result = _refine_translation(full_base_translated, mapping, lang_name, model_name)

    return {
        "original": text.strip(),
        "target_language": lang_name,
        "target_language_native": lang_info["native"],
        "flag": lang_info["flag"],
        "model_used": model_name,
        "base_translation": full_base_translated,
        "improved_translation": llm_result.get("improved_translation", ""),
        "local_context_note": llm_result.get("local_context_note", ""),
        "terminology_glossary": llm_result.get("terminology_glossary", []),
    }
