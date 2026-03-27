"""
Pydantic v2 schemas for all ET-Pulse features.

Each feature has its own request / response model group, clearly
separated by section comments for maintainability.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ================================================================
# Common
# ================================================================


class HealthResponse(BaseModel):
    """Application health check response."""

    status: str = "ok"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ================================================================
# My ET — Personalized News
# ================================================================


class NewsArticle(BaseModel):
    """A single news article."""

    article_id: str = Field(..., description="Unique article identifier")
    title: str
    summary: str
    content: str = ""
    source: str = "Economic Times"
    category: str = ""
    url: str = ""
    published_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(BaseModel):
    """User interest profile for personalized feeds."""

    user_id: str = Field(..., description="Unique user identifier")
    interests: list[str] = Field(
        ...,
        description="List of interest topics (e.g. 'fintech', 'IPO')",
        min_length=1,
    )
    preferred_categories: list[str] = Field(default_factory=list)


class PersonalizedFeedResponse(BaseModel):
    """Response containing personalized news articles."""

    user_id: str
    articles: list[NewsArticle]
    total_results: int
    query_interests: list[str]


class IngestRequest(BaseModel):
    """Request to ingest news articles into the vector store."""

    articles: list[NewsArticle] = Field(
        ...,
        description="Articles to ingest",
        min_length=1,
    )


class IngestResponse(BaseModel):
    """Response after ingesting articles."""

    ingested_count: int
    message: str = "Articles ingested successfully"


# ================================================================
# News Navigator — RAG Q&A
# ================================================================


class NavigatorQuery(BaseModel):
    """A user question for RAG-based Q&A."""

    question: str = Field(
        ...,
        description="Natural language question about business news",
        min_length=3,
    )
    top_k: int = Field(
        default=5,
        description="Number of source documents to retrieve",
        ge=1,
        le=20,
    )


class SourceReference(BaseModel):
    """A reference to a source document used in the answer."""

    article_id: str
    title: str
    relevance_score: float
    url: str = ""


class NavigatorResponse(BaseModel):
    """RAG-synthesized answer with source citations."""

    question: str
    answer: str
    sources: list[SourceReference]
    model_used: str


# ================================================================
# Story Arc Tracker — Timeline & Sentiment
# ================================================================


class StoryArcRequest(BaseModel):
    """Request to analyze a story arc for a given topic."""

    topic: str = Field(
        ...,
        description="Topic or entity to track (e.g. 'Reliance Industries')",
    )
    top_k: int = Field(
        default=10,
        description="Number of related articles to analyze",
        ge=1,
        le=50,
    )


class SentimentLabel(str, Enum):
    """Sentiment classification labels."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class TimelineEvent(BaseModel):
    """A single event in a story timeline."""

    date: str
    headline: str
    summary: str
    sentiment: SentimentLabel
    significance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How significant this event is (0-1)",
    )


class SentimentResult(BaseModel):
    """Overall sentiment analysis of a story arc."""

    overall_sentiment: SentimentLabel
    confidence: float = Field(ge=0.0, le=1.0)
    positive_ratio: float = Field(ge=0.0, le=1.0)
    negative_ratio: float = Field(ge=0.0, le=1.0)
    neutral_ratio: float = Field(ge=0.0, le=1.0)


class StoryArcResponse(BaseModel):
    """Complete story arc analysis with timeline and sentiment."""

    topic: str
    timeline: list[TimelineEvent]
    sentiment_analysis: SentimentResult
    article_count: int
    model_used: str


# ================================================================
# Vernacular Engine — Translation
# ================================================================


class SupportedLanguage(str, Enum):
    """Indian languages supported by the Vernacular Engine."""

    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


class TranslationRequest(BaseModel):
    """Request to translate text to an Indian language."""

    text: str = Field(
        ...,
        description="Text to translate (English source)",
        min_length=1,
    )
    target_language: SupportedLanguage = Field(
        ...,
        description="Target language code",
    )


class GlossaryTerm(BaseModel):
    term: str
    translation: str
    explanation: str


class TranslationResponse(BaseModel):
    """Translation result."""

    original_text: str
    translated_text: str
    source_language: str = "en"
    target_language: str
    engine: str = "llm-dual-pass"
    local_context_note: str = ""
    terminology_glossary: list[GlossaryTerm] = Field(default_factory=list)


# ================================================================
# AI News Video Studio
# ================================================================


class VideoRequest(BaseModel):
    """Request to generate a news video short."""

    article_title: str = Field(..., description="Title of the news article")
    article_content: str = Field(
        ...,
        description="Full article content for script generation",
    )
    duration_seconds: int = Field(
        default=90,
        description="Target video duration (60-120 seconds)",
        ge=60,
        le=120,
    )
    style: str = Field(
        default="professional_news",
        description="Visual style for the video",
    )


class VideoStatusEnum(str, Enum):
    """Video generation status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SCRIPT_ONLY = "script_only"


class VideoScript(BaseModel):
    """Generated video script with visual cues."""

    narration: str
    visual_descriptions: list[str]
    duration_estimate_seconds: int


class VideoResponse(BaseModel):
    """Video generation response."""

    generation_id: str
    status: VideoStatusEnum
    script: VideoScript | None = None
    video_url: str | None = None
    message: str = ""


class VideoStatusResponse(BaseModel):
    """Polling response for video generation status."""

    generation_id: str
    status: VideoStatusEnum
    video_url: str | None = None
    message: str = ""
