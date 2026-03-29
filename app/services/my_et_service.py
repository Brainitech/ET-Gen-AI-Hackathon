"""
My ET Service — Personalized News Feed.

Uses a local sentence-transformers model for embeddings and ChromaDB
as the vector store. Articles are ingested into ChromaDB and then
queried using a user's interest profile for similarity-based ranking.
"""

import logging
import uuid
from datetime import datetime, timezone

import feedparser
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.core.database import get_or_create_collection
from app.models.schemas import (
    IngestResponse,
    NewsArticle,
    PersonalizedFeedResponse,
    UserProfile,
)

logger = logging.getLogger(__name__)

# Lazy-loaded embedding model (shared across requests).
_embedding_model: SentenceTransformer | None = None

COLLECTION_NAME = "et_pulse_articles"


def _get_embedding_model() -> SentenceTransformer:
    """Return the embedding model, loading it on first call."""
    global _embedding_model  # noqa: PLW0603

    if _embedding_model is None:
        settings = get_settings()
        logger.info(
            "Loading embedding model: %s", settings.embedding_model_name
        )
        _embedding_model = SentenceTransformer(settings.embedding_model_name)
    return _embedding_model


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using the sentence-transformers model."""
    model = _get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


def ingest_articles(articles: list[NewsArticle]) -> IngestResponse:
    """Ingest news articles into ChromaDB with embeddings.

    Each article is embedded using its title + summary and stored
    alongside its metadata for later retrieval.
    """
    collection = get_or_create_collection(COLLECTION_NAME)

    texts = [f"{a.title}. {a.summary}" for a in articles]
    embeddings = _embed_texts(texts)

    ids = [a.article_id for a in articles]
    documents = [a.content or a.summary for a in articles]
    metadatas = [
        {
            "title": a.title,
            "summary": a.summary,
            "source": a.source,
            "category": a.category,
            "url": a.url,
            "published_at": a.published_at.isoformat(),
        }
        for a in articles
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    logger.info("Ingested %d articles into ChromaDB", len(articles))
    return IngestResponse(ingested_count=len(articles))


def get_personalized_feed(
    user_id: str,
    interests: list[str],
    top_k: int = 10,
) -> PersonalizedFeedResponse:
    """Retrieve personalized news based on user interests.

    Embeds the user's interests as a single query and performs
    a cosine-similarity search against the article collection.
    """
    collection = get_or_create_collection(COLLECTION_NAME)

    # Combine interests into a single query string for embedding.
    interest_query = ", ".join(interests)
    query_embedding = _embed_texts([interest_query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count() or top_k),
        include=["documents", "metadatas", "distances"],
    )

    articles: list[NewsArticle] = []
    if results and results["metadatas"]:
        for meta, doc in zip(
            results["metadatas"][0],
            results["documents"][0],
        ):
            articles.append(
                NewsArticle(
                    article_id=str(uuid.uuid4()),
                    title=meta.get("title", ""),
                    summary=meta.get("summary", ""),
                    content=doc,
                    source=meta.get("source", ""),
                    category=meta.get("category", ""),
                    url=meta.get("url", ""),
                    published_at=datetime.fromisoformat(
                        meta.get(
                            "published_at",
                            datetime.now(tz=timezone.utc).isoformat(),
                        )
                    ),
                )
            )

    return PersonalizedFeedResponse(
        user_id=user_id,
        articles=articles,
        total_results=len(articles),
        query_interests=interests,
    )


def fetch_rss_articles() -> list[NewsArticle]:
    """Fetch live articles from configured ET RSS feeds.

    Parses each RSS feed and converts entries into ``NewsArticle``
    objects suitable for ingestion.
    """
    settings = get_settings()
    articles: list[NewsArticle] = []

    for feed_url in settings.et_rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                articles.append(
                    NewsArticle(
                        article_id=str(uuid.uuid4()),
                        title=entry.get("title", ""),
                        summary=entry.get("summary", ""),
                        content=entry.get("summary", ""),
                        url=entry.get("link", ""),
                        category=entry.get("category", "general"),
                        published_at=datetime.now(tz=timezone.utc),
                    )
                )
        except Exception:
            logger.exception("Failed to fetch RSS feed: %s", feed_url)

    logger.info("Fetched %d articles from RSS feeds", len(articles))
    return articles
