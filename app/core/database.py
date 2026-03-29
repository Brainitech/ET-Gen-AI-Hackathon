"""
ChromaDB client management.

Provides a singleton persistent ChromaDB client and collection helpers
used by the My ET and News Navigator services.
"""

import logging

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Module-level client reference (initialized on first call).
_chroma_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Return a persistent ChromaDB client (singleton).

    The client persists its data to the directory specified
    by the ``CHROMA_PERSIST_DIR`` environment variable.
    """
    global _chroma_client  # noqa: PLW0603

    if _chroma_client is None:
        settings = get_settings()
        logger.info(
            "Initializing ChromaDB client at: %s",
            settings.chroma_persist_dir,
        )
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


def get_or_create_collection(
    name: str,
    metadata: dict | None = None,
) -> chromadb.Collection:
    """Get or create a ChromaDB collection by name.

    Args:
        name: The collection name.
        metadata: Optional collection metadata (e.g. distance function).

    Returns:
        A ChromaDB ``Collection`` instance.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata=metadata or {"hnsw:space": "cosine"},
    )
