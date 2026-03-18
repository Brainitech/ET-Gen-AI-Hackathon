"""
Story Arc Tracker — Timeline & Sentiment endpoints.

Provides the route for analyzing a topic's story arc, including
timeline extraction and sentiment analysis powered by Groq/Llama 3.
"""

from fastapi import APIRouter

from app.models.schemas import StoryArcRequest, StoryArcResponse
from app.services import story_arc_service

router = APIRouter()


@router.post(
    "/analyze",
    response_model=StoryArcResponse,
    summary="Analyze a topic's story arc",
)
async def analyze_story_arc(
    request: StoryArcRequest,
) -> StoryArcResponse:
    """Analyze a business topic to extract its timeline and sentiment.

    Retrieves related articles and uses Groq/Llama 3 for structured
    extraction of events and sentiment analysis.
    """
    return await story_arc_service.analyze_story_arc(
        topic=request.topic,
        top_k=request.top_k,
    )
