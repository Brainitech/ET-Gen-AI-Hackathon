"""FastAPI endpoint — Vernacular Business News Engine"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.services.vernacular_service import translate_text, SUPPORTED_LANGUAGES

router = APIRouter(prefix="/translate", tags=["Vernacular Engine"])


class TranslateRequest(BaseModel):
    text: str
    target_lang: Literal["hi", "ta", "te", "bn"]


@router.get("/languages")
def list_languages():
    return SUPPORTED_LANGUAGES


@router.post("")
def translate(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    result = translate_text(req.text.strip(), req.target_lang)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result
