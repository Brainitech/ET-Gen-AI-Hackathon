"""
ET-Pulse — Unified FastAPI Application.

This is the single entry-point for the entire platform, registering
all feature routers under the ``/api/v1`` prefix.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.endpoints import (
    my_et,
    news_navigator,
    story_arc,
    vernacular,
    video_studio,
)
from app.core.config import get_settings
from app.core.database import get_chroma_client
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lifespan — startup / shutdown hooks
# ------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: initialize resources on startup."""
    settings = get_settings()

    # Eagerly initialize ChromaDB so the first request is fast.
    logger.info("Initializing ChromaDB persistent client …")
    get_chroma_client()

    logger.info(
        "%s v%s starting on %s:%s",
        settings.app_name,
        settings.app_version,
        settings.app_host,
        settings.app_port,
    )
    yield
    logger.info("Shutting down %s …", settings.app_name)


# ------------------------------------------------------------------
# Application factory
# ------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-native business news platform with personalized feeds, "
        "RAG-based Q&A, story arc tracking, vernacular translations, "
        "and AI video generation — powered entirely by free-tier "
        "and open-source tools."
    ),
    lifespan=lifespan,
)

# ------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Router registration — one per feature, all under /api/v1
# ------------------------------------------------------------------

API_V1_PREFIX = "/api/v1"

app.include_router(
    my_et.router,
    prefix=f"{API_V1_PREFIX}/my-et",
    tags=["My ET — Personalized News"],
)
app.include_router(
    news_navigator.router,
    prefix=f"{API_V1_PREFIX}/navigator",
    tags=["News Navigator — RAG Q&A"],
)
app.include_router(
    story_arc.router,
    prefix=f"{API_V1_PREFIX}/story-arc",
    tags=["Story Arc Tracker"],
)
app.include_router(
    vernacular.router,
    prefix=f"{API_V1_PREFIX}/vernacular",
    tags=["Vernacular Engine — Translation"],
)
app.include_router(
    video_studio.router,
    prefix=f"{API_V1_PREFIX}/video-studio",
    tags=["AI News Video Studio"],
)


# ------------------------------------------------------------------
# Root & Health endpoints
# ------------------------------------------------------------------


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Redirect root to Swagger UI."""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(version=settings.app_version)
