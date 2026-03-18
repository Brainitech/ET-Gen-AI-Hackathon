"""
AI News Video Studio Service — Video Generation.

Generates news video shorts by:
1. Creating a structured video script from article content using Gemini
2. Sending the script to Google Veo API for video generation
3. Providing async polling for generation status

Falls back to script-only mode if Veo quota is exhausted or unavailable.
"""

import json
import logging
import uuid
from datetime import datetime, timezone

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.models.schemas import (
    VideoRequest,
    VideoResponse,
    VideoScript,
    VideoStatusEnum,
    VideoStatusResponse,
)

logger = logging.getLogger(__name__)

# In-memory store for generation tracking.
# In production, replace with Redis or a database.
_generation_store: dict[str, dict] = {}

# Lazy-loaded Gemini client.
_gemini_client: genai.Client | None = None


def _get_gemini_client() -> genai.Client:
    """Return a Gemini client, creating it on first call."""
    global _gemini_client  # noqa: PLW0603

    if _gemini_client is None:
        settings = get_settings()
        _gemini_client = genai.Client(api_key=settings.gemini_api_key)
    return _gemini_client


# ------------------------------------------------------------------
# Script generation
# ------------------------------------------------------------------

SCRIPT_SYSTEM_PROMPT = """You are a professional news video scriptwriter for ET-Pulse.
Given a news article, create a compelling video script for a 60-120 second news short.

Return ONLY valid JSON matching this schema:
{
  "narration": "full narration text for voice-over",
  "visual_descriptions": [
    "description of visual for segment 1",
    "description of visual for segment 2",
    ...
  ],
  "duration_estimate_seconds": 90
}

Guidelines:
- Write clear, engaging narration suitable for text-to-speech
- Break visuals into 10-15 second segments
- Use professional news broadcast tone
- Include data visualizations where appropriate
- Target the specified duration"""


async def _generate_script(
    title: str,
    content: str,
    duration_seconds: int,
) -> VideoScript:
    """Generate a video script using Gemini."""
    settings = get_settings()
    client = _get_gemini_client()

    prompt = (
        f"Article Title: {title}\n\n"
        f"Article Content: {content}\n\n"
        f"Target Duration: {duration_seconds} seconds\n\n"
        "Generate a news video script."
    )

    response = client.models.generate_content(
        model=settings.gemini_model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SCRIPT_SYSTEM_PROMPT,
            temperature=0.4,
            max_output_tokens=2048,
        ),
    )

    raw_text = response.text or "{}"

    # Strip markdown code fences if present.
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1])

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("Failed to parse script JSON: %s", raw_text[:200])
        data = {
            "narration": f"Breaking news: {title}. {content[:300]}",
            "visual_descriptions": [
                "News studio establishing shot",
                "Relevant data charts and graphs",
                "Expert analysis overlay",
                "Summary with key takeaways",
            ],
            "duration_estimate_seconds": duration_seconds,
        }

    return VideoScript(
        narration=data.get("narration", ""),
        visual_descriptions=data.get("visual_descriptions", []),
        duration_estimate_seconds=data.get(
            "duration_estimate_seconds", duration_seconds
        ),
    )


# ------------------------------------------------------------------
# Video generation via Veo API
# ------------------------------------------------------------------


async def _request_veo_generation(
    script: VideoScript,
    style: str,
    generation_id: str,
) -> bool:
    """Request video generation from the Veo API.

    Returns True if the request was accepted, False otherwise.
    The Veo API is async — use ``get_generation_status`` to poll.
    """
    settings = get_settings()

    try:
        client = _get_gemini_client()

        # Compose a visual prompt from the script.
        visual_prompt = (
            f"Create a professional news broadcast video. "
            f"Style: {style}. "
            f"Narration: {script.narration[:500]}. "
            f"Visual scenes: {'; '.join(script.visual_descriptions[:5])}"
        )

        # Use the Veo model for video generation.
        operation = client.models.generate_videos(
            model=settings.veo_model_name,
            prompt=visual_prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
            ),
        )

        # Store the operation for polling.
        _generation_store[generation_id]["veo_operation"] = operation
        _generation_store[generation_id]["status"] = (
            VideoStatusEnum.PROCESSING
        )
        logger.info(
            "Veo generation requested for %s", generation_id
        )
        return True

    except Exception:
        logger.exception(
            "Veo API request failed for %s, falling back to script-only",
            generation_id,
        )
        return False


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


async def generate_video(request: VideoRequest) -> VideoResponse:
    """Generate a news video short from an article.

    Creates a script using Gemini, then requests video generation
    from the Veo API. If Veo is unavailable, returns script-only.

    Args:
        request: The video generation request.

    Returns:
        A ``VideoResponse`` with generation ID and initial status.
    """
    generation_id = str(uuid.uuid4())

    # Initialize tracking entry.
    _generation_store[generation_id] = {
        "status": VideoStatusEnum.PENDING,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "script": None,
        "video_url": None,
        "veo_operation": None,
    }

    # Step 1: Generate the video script.
    script = await _generate_script(
        title=request.article_title,
        content=request.article_content,
        duration_seconds=request.duration_seconds,
    )
    _generation_store[generation_id]["script"] = script

    # Step 2: Request Veo video generation.
    veo_accepted = await _request_veo_generation(
        script=script,
        style=request.style,
        generation_id=generation_id,
    )

    if not veo_accepted:
        _generation_store[generation_id]["status"] = (
            VideoStatusEnum.SCRIPT_ONLY
        )
        return VideoResponse(
            generation_id=generation_id,
            status=VideoStatusEnum.SCRIPT_ONLY,
            script=script,
            message=(
                "Video generation unavailable. "
                "Script has been generated successfully."
            ),
        )

    return VideoResponse(
        generation_id=generation_id,
        status=VideoStatusEnum.PROCESSING,
        script=script,
        message="Video generation in progress. Poll for status.",
    )


async def get_generation_status(
    generation_id: str,
) -> VideoStatusResponse:
    """Check the status of a video generation request.

    Polls the Veo API operation if one exists and updates the
    stored status accordingly.

    Args:
        generation_id: The unique generation ID.

    Returns:
        A ``VideoStatusResponse`` with current status.
    """
    entry = _generation_store.get(generation_id)
    if entry is None:
        return VideoStatusResponse(
            generation_id=generation_id,
            status=VideoStatusEnum.FAILED,
            message="Generation ID not found",
        )

    # If there is a Veo operation, check its status.
    operation = entry.get("veo_operation")
    if operation is not None:
        try:
            # Poll the operation.
            result = operation.result(timeout=5)

            if result and result.generated_videos:
                video = result.generated_videos[0]
                video_url = video.video.uri if video.video else None
                entry["status"] = VideoStatusEnum.COMPLETED
                entry["video_url"] = video_url

                return VideoStatusResponse(
                    generation_id=generation_id,
                    status=VideoStatusEnum.COMPLETED,
                    video_url=video_url,
                    message="Video generation complete",
                )
        except TimeoutError:
            return VideoStatusResponse(
                generation_id=generation_id,
                status=VideoStatusEnum.PROCESSING,
                message="Video is still being generated",
            )
        except Exception as exc:
            logger.exception("Veo polling failed for %s", generation_id)
            entry["status"] = VideoStatusEnum.FAILED
            return VideoStatusResponse(
                generation_id=generation_id,
                status=VideoStatusEnum.FAILED,
                message=f"Generation failed: {exc}",
            )

    return VideoStatusResponse(
        generation_id=generation_id,
        status=VideoStatusEnum(entry["status"]),
        video_url=entry.get("video_url"),
        message="Current status retrieved",
    )
