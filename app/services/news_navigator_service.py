"""
News Navigator Service — RAG-Based Question Answering.

Retrieves relevant articles from ChromaDB using semantic search,
then sends the context to Google Gemini Flash for a grounded,
citation-rich synthesis.
"""

import logging
import uuid

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.core.database import get_or_create_collection
from app.models.schemas import NavigatorResponse, SourceReference
from app.services.my_et_service import COLLECTION_NAME, _embed_texts

logger = logging.getLogger(__name__)

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
# RAG Pipeline
# ------------------------------------------------------------------

RAG_SYSTEM_PROMPT = (
    "You are ET-Pulse News Navigator, an expert AI analyst for Indian "
    "business news. Answer the user's question using ONLY the provided "
    "context articles. Cite specific articles by their title when "
    "referencing information. If the context does not contain enough "
    "information, say so clearly. Be concise, factual, and professional."
)


def _build_context(
    metadatas: list[dict],
    documents: list[str],
) -> str:
    """Build a context string from retrieved documents."""
    context_parts: list[str] = []
    for i, (meta, doc) in enumerate(zip(metadatas, documents), 1):
        title = meta.get("title", "Untitled")
        source = meta.get("source", "Unknown")
        context_parts.append(
            f"[Article {i}] Title: {title}\nSource: {source}\n"
            f"Content: {doc}\n"
        )
    return "\n---\n".join(context_parts)


async def query_navigator(
    question: str,
    top_k: int = 5,
) -> NavigatorResponse:
    """Execute the full RAG pipeline: retrieve → augment → generate.

    Args:
        question: The user's natural-language question.
        top_k: Number of source documents to retrieve.

    Returns:
        A ``NavigatorResponse`` with the synthesized answer and sources.
    """
    settings = get_settings()

    # Step 1: Retrieve relevant documents from ChromaDB.
    collection = get_or_create_collection(COLLECTION_NAME)
    query_embedding = _embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count() or top_k),
        include=["documents", "metadatas", "distances"],
    )

    metadatas = results["metadatas"][0] if results["metadatas"] else []
    documents = results["documents"][0] if results["documents"] else []
    distances = results["distances"][0] if results["distances"] else []

    # Step 2: Build context and source references.
    context = _build_context(metadatas, documents)
    sources: list[SourceReference] = []
    for meta, distance in zip(metadatas, distances):
        sources.append(
            SourceReference(
                article_id=str(uuid.uuid4()),
                title=meta.get("title", "Untitled"),
                relevance_score=round(1.0 - distance, 4),
                url=meta.get("url", ""),
            )
        )

    # Step 3: Generate answer using Gemini Flash.
    client = _get_gemini_client()
    user_prompt = (
        f"Context Articles:\n{context}\n\n"
        f"User Question: {question}\n\n"
        "Provide a comprehensive answer with citations."
    )

    response = client.models.generate_content(
        model=settings.gemini_model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=RAG_SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=2048,
        ),
    )

    answer = response.text or "Unable to generate an answer at this time."

    return NavigatorResponse(
        question=question,
        answer=answer,
        sources=sources,
        model_used=settings.gemini_model_name,
    )
