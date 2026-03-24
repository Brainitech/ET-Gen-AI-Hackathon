"""
aether_ai — FastAPI Application Root
Three AI-native news features: Story Arc Tracker, News Summarizer, Vernacular Engine
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import story_arc, summarizer, vernacular, articles

app = FastAPI(
    title="aether_ai — AI-Native News Engine",
    description=(
        "ET Hackathon Round 2 | "
        "Story Arc Tracker · News Summarizer · Vernacular Business News Engine"
    ),
    version="2.0.0",
)

# CORS — allow Streamlit frontend on any port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
PREFIX = "/api/v1"
app.include_router(story_arc.router, prefix=PREFIX)
app.include_router(summarizer.router, prefix=PREFIX)
app.include_router(vernacular.router, prefix=PREFIX)
app.include_router(articles.router, prefix=PREFIX)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "2.0.0", "project": "aether_ai"}


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "aether_ai API is running",
        "docs": "/docs",
        "endpoints": {
            "story_arc": "/api/v1/story-arc",
            "summarize": "/api/v1/summarize",
            "translate": "/api/v1/translate",
        },
    }
