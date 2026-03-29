"""FastAPI endpoint — Story Arc Tracker"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.story_arc_service import build_story_arc

router = APIRouter(prefix="/story-arc", tags=["Story Arc Tracker"])


class StoryArcRequest(BaseModel):
    topic: str


@router.post("")
def get_story_arc(req: StoryArcRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    result = build_story_arc(req.topic.strip())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
