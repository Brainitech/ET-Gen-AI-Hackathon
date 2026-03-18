"""
AI News Video Studio — Video Generation endpoints.

Provides routes for:
- Requesting a news video short generation
- Polling the generation status
"""

from fastapi import APIRouter

from app.models.schemas import (
    VideoRequest,
    VideoResponse,
    VideoStatusResponse,
)
from app.services import video_studio_service

router = APIRouter()


@router.post(
    "/generate",
    response_model=VideoResponse,
    summary="Generate a news video short",
)
async def generate_video(request: VideoRequest) -> VideoResponse:
    """Request generation of a 60-120 second AI news video.

    Creates a script using Gemini and requests video generation
    from the Veo API. If Veo is unavailable, returns script-only.
    """
    return await video_studio_service.generate_video(request)


@router.get(
    "/status/{generation_id}",
    response_model=VideoStatusResponse,
    summary="Check video generation status",
)
async def get_status(generation_id: str) -> VideoStatusResponse:
    """Poll the status of a video generation request.

    Returns the current status and video URL when complete.
    """
    return await video_studio_service.get_generation_status(generation_id)
