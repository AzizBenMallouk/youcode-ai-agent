from functools import lru_cache

from qdrant_client import (
    QdrantClient,
)

from youcode_ai.core.config import (
    settings,
)


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    client_arguments = {
        "url": settings.qdrant_url,
        "timeout": (
            settings.external_api_timeout
        ),
    }

    if settings.qdrant_api_key:
        client_arguments["api_key"] = (
            settings.qdrant_api_key
        )

    return QdrantClient(
        **client_arguments
    )


def check_qdrant_connection() -> bool:
    try:
        client = get_qdrant_client()

        client.get_collections()

        return True
    except Exception:
        return False