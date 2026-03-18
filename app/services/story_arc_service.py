"""
Story Arc Tracker Service — Timeline & Sentiment Analysis.

Retrieves related articles from ChromaDB, then uses Groq's ultra-fast
Llama 3 inference to extract a structured timeline of events and
perform sentiment analysis.
"""

import json
import logging
import uuid

from groq import Groq

from app.core.config import get_settings
from app.core.database import get_or_create_collection
from app.models.schemas import (
    SentimentLabel,
    SentimentResult,
    StoryArcResponse,
    TimelineEvent,
)
from app.services.my_et_service import COLLECTION_NAME, _embed_texts

logger = logging.getLogger(__name__)

# Lazy-loaded Groq client.
_groq_client: Groq | None = None


def _get_groq_client() -> Groq:
    """Return a Groq client, creating it on first call."""
    global _groq_client  # noqa: PLW0603

    if _groq_client is None:
        settings = get_settings()
        _groq_client = Groq(api_key=settings.groq_api_key)
    return _groq_client


# ------------------------------------------------------------------
# Groq prompt for structured extraction
# ------------------------------------------------------------------

STORY_ARC_SYSTEM_PROMPT = """You are a business news analyst. Given a set of articles about a topic, extract:

1. A timeline of key events (date, headline, summary, sentiment, significance_score 0-1)
2. An overall sentiment analysis

Return ONLY valid JSON matching this exact schema:
{
  "timeline": [
    {
      "date": "YYYY-MM-DD or descriptive date",
      "headline": "short headline",
      "summary": "1-2 sentence summary",
      "sentiment": "positive|negative|neutral|mixed",
      "significance_score": 0.0-1.0
    }
  ],
  "sentiment_analysis": {
    "overall_sentiment": "positive|negative|neutral|mixed",
    "confidence": 0.0-1.0,
    "positive_ratio": 0.0-1.0,
    "negative_ratio": 0.0-1.0,
    "neutral_ratio": 0.0-1.0
  }
}

Sort timeline events chronologically. Be precise and factual."""


async def analyze_story_arc(
    topic: str,
    top_k: int = 10,
) -> StoryArcResponse:
    """Analyze a topic's story arc using Groq/Llama 3.

    Args:
        topic: The entity or topic to track.
        top_k: Number of related articles to analyze.

    Returns:
        A ``StoryArcResponse`` with timeline events and sentiment.
    """
    settings = get_settings()

    # Step 1: Retrieve relevant articles from ChromaDB.
    collection = get_or_create_collection(COLLECTION_NAME)
    query_embedding = _embed_texts([topic])[0]

    count = collection.count()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count) if count > 0 else top_k,
        include=["documents", "metadatas"],
    )

    metadatas = results["metadatas"][0] if results["metadatas"] else []
    documents = results["documents"][0] if results["documents"] else []

    # Step 2: Build article context for Groq.
    article_context_parts: list[str] = []
    for i, (meta, doc) in enumerate(zip(metadatas, documents), 1):
        title = meta.get("title", "Untitled")
        published = meta.get("published_at", "Unknown date")
        article_context_parts.append(
            f"Article {i}: {title} (Published: {published})\n{doc}"
        )
    article_context = "\n\n---\n\n".join(article_context_parts)

    # Step 3: Call Groq/Llama 3 for structured extraction.
    client = _get_groq_client()
    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Articles:\n{article_context}\n\n"
        "Analyze these articles and extract the story arc."
    )

    response = client.chat.completions.create(
        model=settings.groq_model_name,
        messages=[
            {"role": "system", "content": STORY_ARC_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )

    # Step 4: Parse the structured JSON response.
    raw_text = response.choices[0].message.content or "{}"

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.error("Failed to parse Groq response as JSON: %s", raw_text)
        data = {"timeline": [], "sentiment_analysis": {}}

    # Build timeline events.
    timeline: list[TimelineEvent] = []
    for event in data.get("timeline", []):
        try:
            timeline.append(
                TimelineEvent(
                    date=event.get("date", "Unknown"),
                    headline=event.get("headline", ""),
                    summary=event.get("summary", ""),
                    sentiment=SentimentLabel(
                        event.get("sentiment", "neutral")
                    ),
                    significance_score=float(
                        event.get("significance_score", 0.5)
                    ),
                )
            )
        except (ValueError, KeyError):
            logger.warning("Skipping malformed timeline event: %s", event)

    # Build sentiment result.
    sa = data.get("sentiment_analysis", {})
    sentiment_analysis = SentimentResult(
        overall_sentiment=SentimentLabel(
            sa.get("overall_sentiment", "neutral")
        ),
        confidence=float(sa.get("confidence", 0.5)),
        positive_ratio=float(sa.get("positive_ratio", 0.33)),
        negative_ratio=float(sa.get("negative_ratio", 0.33)),
        neutral_ratio=float(sa.get("neutral_ratio", 0.34)),
    )

    return StoryArcResponse(
        topic=topic,
        timeline=timeline,
        sentiment_analysis=sentiment_analysis,
        article_count=len(metadatas),
        model_used=settings.groq_model_name,
    )
