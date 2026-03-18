"""
My ET — Personalized News Feed endpoints.

Provides routes for:
- Creating / updating user interest profiles
- Ingesting news articles into the vector store
- Retrieving personalized feeds
- Ingesting live RSS feed data
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    IngestRequest,
    IngestResponse,
    PersonalizedFeedResponse,
    UserProfile,
)
from app.services import my_et_service

router = APIRouter()

# In-memory profile store (replace with DB in production).
_profiles: dict[str, UserProfile] = {}


@router.post(
    "/profile",
    response_model=UserProfile,
    summary="Create or update a user interest profile",
)
async def upsert_profile(profile: UserProfile) -> UserProfile:
    """Store a user's interest profile for personalized news."""
    _profiles[profile.user_id] = profile
    return profile


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest news articles into the vector store",
)
async def ingest_articles(request: IngestRequest) -> IngestResponse:
    """Ingest a batch of articles into ChromaDB for retrieval."""
    return my_et_service.ingest_articles(request.articles)


@router.get(
    "/feed/{user_id}",
    response_model=PersonalizedFeedResponse,
    summary="Get personalized news feed",
)
async def get_feed(
    user_id: str,
    top_k: int = Query(default=10, ge=1, le=50),
) -> PersonalizedFeedResponse:
    """Retrieve a personalized news feed based on user interests."""
    profile = _profiles.get(user_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found for user_id: {user_id}",
        )

    return my_et_service.get_personalized_feed(
        user_id=user_id,
        interests=profile.interests,
        top_k=top_k,
    )


@router.post(
    "/ingest-rss",
    response_model=IngestResponse,
    summary="Fetch and ingest live RSS feeds",
)
async def ingest_rss_feeds() -> IngestResponse:
    """Fetch articles from configured ET RSS feeds and ingest them."""
    articles = my_et_service.fetch_rss_articles()
    if not articles:
        return IngestResponse(
            ingested_count=0,
            message="No articles fetched from RSS feeds",
        )
    return my_et_service.ingest_articles(articles)
