"""
Vernacular Engine Service — Indian Language Translation.

Integrates AI4Bharat's IndicTrans2 for culturally adapted translations
of English text into Indian languages. Falls back to Gemini-based
translation if the IndicTrans2 model is unavailable.
"""

import logging

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.models.schemas import SupportedLanguage, TranslationResponse

logger = logging.getLogger(__name__)

# Language code → full name mapping for prompts.
LANGUAGE_NAMES: dict[str, str] = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "or": "Odia",
}

# IndicTrans2 model reference (lazy-loaded).
_indictrans_model = None
_indictrans_tokenizer = None
_indictrans_available: bool | None = None


def _try_load_indictrans2() -> bool:
    """Attempt to load the IndicTrans2 model.

    Returns True if successful, False otherwise. The result is cached
    so subsequent calls are instant.
    """
    global _indictrans_model, _indictrans_tokenizer  # noqa: PLW0603
    global _indictrans_available  # noqa: PLW0603

    if _indictrans_available is not None:
        return _indictrans_available

    settings = get_settings()
    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        model_path = settings.indictrans2_model_dir
        logger.info("Loading IndicTrans2 model from: %s", model_path)

        _indictrans_tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True
        )
        _indictrans_model = AutoModelForSeq2SeqLM.from_pretrained(
            model_path, trust_remote_code=True
        )
        _indictrans_available = True
        logger.info("IndicTrans2 model loaded successfully")

    except Exception:
        logger.warning(
            "IndicTrans2 model not available, will use Gemini fallback. "
            "To use IndicTrans2, download the model to: %s",
            settings.indictrans2_model_dir,
        )
        _indictrans_available = False

    return _indictrans_available


def _translate_with_indictrans2(
    text: str,
    target_lang: str,
) -> str:
    """Translate using the local IndicTrans2 model.

    Uses the HuggingFace transformers interface for IndicTrans2's
    encoder-decoder architecture.
    """
    if _indictrans_tokenizer is None or _indictrans_model is None:
        raise RuntimeError("IndicTrans2 model not loaded")

    # IndicTrans2 expects language tags in the input.
    lang_name = LANGUAGE_NAMES.get(target_lang, "Hindi")
    prompt = f"Translate from English to {lang_name}: {text}"

    inputs = _indictrans_tokenizer(
        prompt,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    )

    generated = _indictrans_model.generate(
        **inputs,
        max_new_tokens=512,
        num_beams=5,
        length_penalty=1.0,
    )

    translated = _indictrans_tokenizer.decode(
        generated[0], skip_special_tokens=True
    )
    return translated


async def _translate_with_gemini(
    text: str,
    target_lang: str,
) -> str:
    """Fallback: translate using Google Gemini."""
    settings = get_settings()
    lang_name = LANGUAGE_NAMES.get(target_lang, "Hindi")

    client = genai.Client(api_key=settings.gemini_api_key)

    prompt = (
        f"Translate the following English text to {lang_name}. "
        f"Provide ONLY the translation, no explanations or notes. "
        f"Ensure the translation is culturally appropriate for an "
        f"Indian audience reading business news.\n\n"
        f"Text: {text}"
    )

    response = client.models.generate_content(
        model=settings.gemini_model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=1024,
        ),
    )

    return response.text or text


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


async def translate_text(
    text: str,
    target_language: SupportedLanguage,
) -> TranslationResponse:
    """Translate English text to the specified Indian language.

    Tries IndicTrans2 first for quality translations, then falls
    back to Gemini if the model is not available.

    Args:
        text: English source text.
        target_language: Target language enum value.

    Returns:
        A ``TranslationResponse`` with the translated text.
    """
    target_lang = target_language.value
    engine = "indictrans2"

    if _try_load_indictrans2():
        try:
            translated = _translate_with_indictrans2(text, target_lang)
        except Exception:
            logger.exception("IndicTrans2 translation failed, using Gemini")
            translated = await _translate_with_gemini(text, target_lang)
            engine = "gemini_fallback"
    else:
        translated = await _translate_with_gemini(text, target_lang)
        engine = "gemini_fallback"

    return TranslationResponse(
        original_text=text,
        translated_text=translated,
        source_language="en",
        target_language=target_lang,
        engine=engine,
    )
