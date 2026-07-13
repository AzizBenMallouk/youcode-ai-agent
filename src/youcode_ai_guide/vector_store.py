from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from youcode_ai_guide.config import Settings


def create_qdrant_client(
    settings: Settings,
) -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
    )


def create_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
    recreate: bool = False,
) -> None:
    collection_exists = client.collection_exists(
        collection_name=collection_name
    )

    if collection_exists and recreate:
        client.delete_collection(
            collection_name=collection_name
        )

        collection_exists = False

    if not collection_exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Collection créée : {collection_name}"
        )

    else:
        print(
            f"Collection déjà existante : {collection_name}"
        )


def create_vector_store(
    client: QdrantClient,
    settings: Settings,
    embeddings: OllamaEmbeddings,
) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings,
    )