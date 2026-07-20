from qdrant_client import QdrantClient
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    VectorParams,
)

from youcode_guide.config import settings

def create_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
    )


def ensure_collection(
    *,
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    if client.collection_exists(
        collection_name
    ):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def ensure_vector_collections(
    *,
    client: QdrantClient,
    vector_size: int,
) -> None:
    ensure_collection(
        client=client,
        collection_name=(
            settings.qdrant_document_collection
        ),
        vector_size=vector_size,
    )

    ensure_collection(
        client=client,
        collection_name=(
            settings.qdrant_gap_collection
        ),
        vector_size=vector_size,
    )
