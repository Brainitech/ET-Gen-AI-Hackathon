"""FastAPI endpoint — News Summarizer"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.summarizer_service import summarize

router = APIRouter(prefix="/summarize", tags=["News Summarizer"])


class SummarizeRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


@router.post("")
def summarize_article(req: SummarizeRequest):
    if not req.text and not req.url:
        raise HTTPException(status_code=400, detail="Provide either 'text' or 'url'.")
    result = summarize(text=req.text, url=req.url)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result
