from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from youcode_guide.config import settings


def create_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
    )


def detect_embedding_dimension(
    embedding_model: Embeddings,
) -> int:
    test_vector = embedding_model.embed_query(
        "YouCode embedding dimension test"
    )

    if not test_vector:
        raise ValueError(
            "The embedding model returned "
            "an empty vector."
        )

    return len(test_vector)


def recreate_collection(
    client: QdrantClient,
    embedding_model: Embeddings,
) -> int:
    collection_name = (
        settings.qdrant_collection
    )

    vector_size = detect_embedding_dimension(
        embedding_model
    )

    if client.collection_exists(
        collection_name
    ):
        client.delete_collection(
            collection_name=collection_name
        )

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    return vector_size


def create_vector_store(
    client: QdrantClient,
    embedding_model: Embeddings,
) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=(
            settings.qdrant_collection
        ),
        embedding=embedding_model,
    )