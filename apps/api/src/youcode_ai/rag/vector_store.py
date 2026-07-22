from langchain_core.embeddings import (
    Embeddings,
)
from langchain_qdrant import (
    QdrantVectorStore,
)
from qdrant_client import (
    QdrantClient,
)
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from youcode_ai.core.config import (
    settings,
)
from youcode_ai.core.llm import (
    create_embedding_model,
)
from youcode_ai.infrastructure.vector import (
    get_qdrant_client,
)


def detect_embedding_dimension(
    embeddings: Embeddings,
) -> int:
    test_vector = embeddings.embed_query(
        "YouCode embedding dimension test"
    )

    if not test_vector:
        raise RuntimeError(
            "The embedding model returned "
            "an empty vector."
        )

    return len(test_vector)


def recreate_document_collection(
    *,
    client: QdrantClient,
    embeddings: Embeddings,
) -> int:
    """
    Supprime puis recrée la collection.

    Cette fonction doit uniquement être appelée
    par le script d'ingestion.
    """

    collection_name = (
        settings
        .qdrant_documents_collection
    )

    vector_size = (
        detect_embedding_dimension(
            embeddings
        )
    )

    if client.collection_exists(
        collection_name=collection_name
    ):
        client.delete_collection(
            collection_name=(
                collection_name
            )
        )

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    return vector_size


def create_document_vector_store(
    *,
    client: QdrantClient | None = None,
    embeddings: Embeddings | None = None,
) -> QdrantVectorStore:
    effective_client = (
        client
        or get_qdrant_client()
    )

    effective_embeddings = (
        embeddings
        or create_embedding_model()
    )

    collection_name = (
        settings
        .qdrant_documents_collection
    )

    if not effective_client.collection_exists(
        collection_name=collection_name
    ):
        raise RuntimeError(
            "The Qdrant document collection "
            f"'{collection_name}' does not "
            "exist. Run document ingestion "
            "first."
        )

    return QdrantVectorStore(
        client=effective_client,
        collection_name=collection_name,
        embedding=effective_embeddings,
    )