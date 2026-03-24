"""
aether_ai — Vernacular Business News Engine

Translates English business news into Hindi, Tamil, Telugu, Bengali with:
  - Accurate base translation via deep-translator (Google Translate, free)
  - LLM-powered naturalness post-processing (business terminology adaptation)
  - Local cultural context note explaining financial terms to local readers
  - Business terminology glossary extraction
"""
import re
import json
from typing import Any, Dict, List
from deep_translator import GoogleTranslator
from app.core.config import get_llm_client

SUPPORTED_LANGUAGES = {
    "hi": {"name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇮🇳"},
}

# Common business terms that need cultural adaptation rather than literal translation
BUSINESS_TERMS = [
    "mutual fund", "sensex", "nifty", "IPO", "FDI", "FPI", "SEBI", "RBI",
    "unicorn", "startup", "venture capital", "angel investor", "hedge fund",
    "NSE", "BSE", "MSME", "GST", "fiscal deficit", "repo rate", "CRR",
    "inflation", "GDP", "CAGR", "EBITDA", "P/E ratio", "market cap",
]


def _translate_base(text: str, target_lang: str) -> str:
    """Base translation using Google Translate (free, no API key)."""
    try:
        translator = GoogleTranslator(source="en", target=target_lang)
        # Google Translate has a ~5000 char limit per call
        if len(text) <= 4500:
            return translator.translate(text)
        # Chunk for longer texts
        chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
        return " ".join(translator.translate(chunk) for chunk in chunks)
    except Exception as e:
        return f"[Translation error: {str(e)}]"


def _post_process_and_contextualise(
    original: str,
    translated: str,
    target_lang: str,
) -> Dict[str, Any]:
    """
    Use LLM to:
    1. Make the translation sound natural for business readers
    2. Generate a local context note
    3. Extract a terminology glossary
    """
    lang_info = SUPPORTED_LANGUAGES.get(target_lang, {"name": target_lang, "native": target_lang})
    lang_name = lang_info["name"]

    # Find which business terms appear in the original
    found_terms = [t for t in BUSINESS_TERMS if t.lower() in original.lower()]
    terms_str = ", ".join(found_terms) if found_terms else "general financial terms"

    prompt = f"""You are a bilingual business news editor specialising in {lang_name}.

ORIGINAL ENGLISH TEXT:
{original[:2000]}

RAW MACHINE TRANSLATION ({lang_name}):
{translated[:2000]}

The text contains these business/financial terms: {terms_str}

Respond in this exact JSON format (no markdown fences):
{{
  "improved_translation": "A polished {lang_name} translation that sounds natural to a local business reader. Keep domain-specific English terms like SEBI, RBI, GDP, IPO as-is (they are widely understood). Adapt idioms and phrasing to feel local, not literal.",
  "local_context_note": "A 2-3 sentence note in English explaining the story with cultural/local context that a {lang_name}-speaking reader in India would appreciate. Mention local relevance, comparison to similar Indian scenarios, or how it affects common people.",
  "terminology_glossary": [
    {{"term": "English term", "translation": "{lang_name} translation or transliteration", "explanation": "plain-language explanation in English"}}
  ]
}}

Rules:
- improved_translation must be in {lang_name} script
- terminology_glossary should cover 3-5 key financial terms from the text
- Return ONLY the JSON, no extra text"""

    client, model = get_llm_client()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        parsed = json.loads(raw)
        return parsed
    except Exception:
        # Fallback: return base translation without LLM enhancement
        return {
            "improved_translation": translated,
            "local_context_note": "LLM post-processing unavailable — showing base machine translation.",
            "terminology_glossary": [],
        }


def translate_text(text: str, target_lang: str) -> Dict[str, Any]:
    """
    Full vernacular translation pipeline.
    Returns: translated text, local context note, terminology glossary.
    """
    if target_lang not in SUPPORTED_LANGUAGES:
        return {"error": f"Unsupported language '{target_lang}'. Choose: hi, ta, te, bn"}

    if not text or len(text.strip()) < 10:
        return {"error": "Text too short to translate."}

    lang_info = SUPPORTED_LANGUAGES[target_lang]

    # Step 1: Base machine translation
    base_translation = _translate_base(text.strip(), target_lang)

    # Step 2: LLM post-processing for naturalness + context
    llm_result = _post_process_and_contextualise(text.strip(), base_translation, target_lang)

    return {
        "original": text.strip(),
        "target_language": lang_info["name"],
        "target_language_native": lang_info["native"],
        "flag": lang_info["flag"],
        "base_translation": base_translation,
        "improved_translation": llm_result.get("improved_translation", base_translation),
        "local_context_note": llm_result.get("local_context_note", ""),
        "terminology_glossary": llm_result.get("terminology_glossary", []),
    }
