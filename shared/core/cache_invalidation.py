"""
Cache invalidation utilities for the semantic cache.

Call invalidate_semantic_cache() after updating YouCode documents
(PDF, Markdown) to force the Guide agent to generate fresh answers
from the new content instead of serving stale cached responses.
"""

import logging

from qdrant_client import QdrantClient
from shared.core.config import settings

logger = logging.getLogger(__name__)


def invalidate_semantic_cache() -> bool:
    """
    Delete the entire semantic cache collection in Qdrant.

    LiteLLM will automatically recreate the collection on the
    next cache miss, so this is safe to call at any time.

    Returns:
        True if the collection was deleted, False if it didn't exist.
    """
    try:
        client = QdrantClient(url=settings.qdrant_url)
        collection_name = settings.semantic_cache_collection

        collections = [c.name for c in client.get_collections().collections]

        if collection_name in collections:
            client.delete_collection(collection_name)
            logger.info(
                "Semantic cache collection '%s' invalidated successfully.",
                collection_name,
            )
            return True

        logger.info(
            "Semantic cache collection '%s' does not exist, nothing to invalidate.",
            collection_name,
        )
        return False

    except Exception:
        logger.exception("Failed to invalidate semantic cache.")
        return False
