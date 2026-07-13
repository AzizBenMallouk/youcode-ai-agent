from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from youcode_ai_guide.config import Settings
from youcode_ai_guide.embeddings import create_embeddings
from youcode_ai_guide.vector_store import (
    create_qdrant_client,
    create_vector_store,
)


SearchResult = tuple[Document, float]


def create_retriever_store(
    settings: Settings,
) -> QdrantVectorStore:
    client = create_qdrant_client(settings)

    collection_exists = client.collection_exists(
        collection_name=settings.qdrant_collection
    )

    if not collection_exists:
        raise RuntimeError(
            "La collection Qdrant n'existe pas. "
            "Exécute d'abord l'indexation."
        )

    embeddings = create_embeddings(settings)

    return create_vector_store(
        client=client,
        settings=settings,
        embeddings=embeddings,
    )


def search_documents(
    question: str,
    vector_store: QdrantVectorStore,
    k: int = 3,
    score_threshold: float = 0.40,
) -> list[SearchResult]:
    clean_question = question.strip()

    if not clean_question:
        return []

    results = vector_store.similarity_search_with_score(
        query=clean_question,
        k=k,
    )

    relevant_results = [
        (document, score)
        for document, score in results
        if score >= score_threshold
    ]

    return relevant_results