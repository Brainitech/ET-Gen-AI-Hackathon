"""
Vernacular Engine — Translation endpoints.

Provides the route for translating English business news text
into Indian languages using IndicTrans2 or Gemini fallback.
"""

from fastapi import APIRouter

from app.models.schemas import TranslationRequest, TranslationResponse
from app.services import vernacular_service

router = APIRouter()


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate text to an Indian language",
)
async def translate_text(
    request: TranslationRequest,
) -> TranslationResponse:
    """Translate English text to the specified Indian language.

    Uses AI4Bharat's IndicTrans2 model for culturally adapted
    translations. Falls back to Gemini if the model is unavailable.
    """
    return await vernacular_service.translate_text(
        text=request.text,
        target_language=request.target_language,
    )
