"""
My ET — Extended FastAPI endpoints.

Adds to the existing app/api/v1/endpoints/my_et.py:
  POST /api/v1/my-et/profile/extended   — save extended profile
  GET  /api/v1/my-et/briefing/{user_id} — AI-enriched personalized feed
  POST /api/v1/my-et/deep-dive          — full article breakdown
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services.my_et_ai_service import (
    build_personalized_briefing,
    generate_deep_dive,
    generate_persona_snippet,
)

# Import new schemas (add these to app/models/schemas.py)
from app.models.my_et_schemas import (
    DeepDiveRequest,
    DeepDiveResponse,
    DeepDiveSection,
    ExtendedUserProfile,
    BriefingResponse,
)

router = APIRouter(prefix="/my-et", tags=["My ET"])

# In-memory extended profile store (replace with DB in production)
_extended_profiles: dict[str, ExtendedUserProfile] = {}


# ── 1. Save Extended Profile ──────────────────────────────────────

@router.post("/profile/extended", response_model=ExtendedUserProfile)
async def save_extended_profile(profile: ExtendedUserProfile) -> ExtendedUserProfile:
    """
    Save a rich user profile with persona type and context.
    Also auto-populates the interests list based on persona if empty.
    """
    # Auto-generate interests from persona context if not provided
    if not profile.interests:
        profile.interests = _derive_interests(profile)

    _extended_profiles[profile.user_id] = profile
    return profile


# ── 2. Get Personalized Briefing ──────────────────────────────────

@router.get("/briefing/{user_id}")
async def get_briefing(user_id: str, top_n: int = 5) -> dict:
    """
    Return an AI-enriched personalized news briefing.
    Top N articles get auto-generated persona snippets.
    Remaining articles are returned snippet_ready=False for lazy loading.
    """
    profile = _extended_profiles.get(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"No extended profile found for user_id: {user_id}. "
                   f"POST to /my-et/profile/extended first.",
        )

    briefing = build_personalized_briefing(
        user_id=user_id,
        persona_type=profile.persona_type.value,
        interests=profile.interests,
        context_summary=profile.get_context_summary(),
        top_n_enriched=top_n,
    )
    return briefing


# ── 3. Lazy Snippet — single article on demand ────────────────────

@router.post("/snippet")
async def get_snippet(
    user_id: str,
    article_title: str,
    article_summary: str,
) -> dict:
    """
    Generate a persona snippet for a single article on demand.
    Used for lazy loading articles beyond the initial top N.
    """
    profile = _extended_profiles.get(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")

    snippet = generate_persona_snippet(
        article_title=article_title,
        article_summary=article_summary,
        persona_type=profile.persona_type.value,
        context_summary=profile.get_context_summary(),
    )
    return {"snippet": snippet, "snippet_ready": True}


# ── 4. Deep Dive ──────────────────────────────────────────────────

@router.post("/deep-dive", response_model=DeepDiveResponse)
async def deep_dive(req: DeepDiveRequest) -> DeepDiveResponse:
    """
    Full contextual breakdown of a single article for the user's persona.
    Returns 4 persona-specific sections + a bottom line takeaway.
    """
    profile = _extended_profiles.get(req.user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found.")

    result = generate_deep_dive(
        article_title=req.article_title,
        article_summary=req.article_summary,
        persona_type=profile.persona_type.value,
        context_summary=profile.get_context_summary(),
    )

    return DeepDiveResponse(
        article_title=req.article_title,
        persona_type=profile.persona_type.value,
        sections=[
            DeepDiveSection(
                heading=s["heading"],
                content=s["content"],
            )
            for s in result.get("sections", [])
        ],
        bottom_line=result.get("bottom_line", ""),
    )


# ── Helper — derive interests from persona context ────────────────

def _derive_interests(profile: ExtendedUserProfile) -> list[str]:
    """Auto-generate interest keywords from persona context."""
    interests: list[str] = []

    if profile.investor_context:
        ctx = profile.investor_context
        interests.extend(ctx.portfolio_sectors)
        interests.extend(ctx.tracked_stocks)
        interests.extend(["markets", "sensex", "nifty", "stocks", "mutual fund"])

    elif profile.founder_context:
        ctx = profile.founder_context
        interests.extend([ctx.startup_sector, "startup", "funding", "venture capital"])
        interests.extend(ctx.competitors)

    elif profile.student_context:
        ctx = profile.student_context
        interests.extend([ctx.field_of_study, ctx.career_goal, "economy", "business"])

    elif profile.executive_context:
        ctx = profile.executive_context
        interests.extend([ctx.industry, ctx.function])
        interests.extend(ctx.strategic_focus)
        interests.extend(["corporate", "strategy", "policy"])

    # Filter blanks
    return [i.strip() for i in interests if i.strip()]
