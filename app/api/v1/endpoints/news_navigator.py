"""
News Navigator — RAG-Based Q&A endpoints.

Provides the interactive question-answering route that queries
the ChromaDB vector store and synthesizes answers using Gemini.
"""

from fastapi import APIRouter

from app.models.schemas import NavigatorQuery, NavigatorResponse
from app.services import news_navigator_service

router = APIRouter()


@router.post(
    "/query",
    response_model=NavigatorResponse,
    summary="Ask a question about business news",
)
async def query_news(query: NavigatorQuery) -> NavigatorResponse:
    """Submit a question and receive a RAG-synthesized answer.

    The system retrieves relevant news articles from the vector
    store and uses Gemini Flash to generate a cited answer.
    """
    return await news_navigator_service.query_navigator(
        question=query.question,
        top_k=query.top_k,
    )
