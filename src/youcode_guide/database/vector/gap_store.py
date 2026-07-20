from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from youcode_guide.config import settings


def create_gap_vector_store(
    *,
    client: QdrantClient,
    embeddings: Embeddings,
) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=(
            settings.qdrant_gap_collection
        ),
        embedding=embeddings,
    )