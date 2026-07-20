from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
)

from youcode_guide.config import settings


def create_document_vector_store(
    *,
    client: QdrantClient,
    embeddings: Embeddings,
) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=(
            settings.qdrant_document_collection
        ),
        embedding=embeddings,
    )


def delete_document_vectors(
    *,
    client: QdrantClient,
    document_id: str,
) -> None:
    client.delete(
        collection_name=(
            settings.qdrant_document_collection
        ),
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key=(
                            "metadata.document_id"
                        ),
                        match=MatchValue(
                            value=document_id,
                        ),
                    )
                ]
            )
        ),
    )