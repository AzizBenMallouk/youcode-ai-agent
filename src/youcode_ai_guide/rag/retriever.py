from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_core.vectorstores import (
    VectorStoreRetriever,
)

from youcode_ai_guide.config import Settings
from youcode_ai_guide.embeddings import create_embeddings
from youcode_ai_guide.vector_store import (
    create_qdrant_client,
    create_vector_store,
)
from qdrant_client import models


SearchResult = tuple[Document, float]


def create_category_filter(
    category: str,
) -> models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.category",
                match=models.MatchValue(
                    value=category,
                ),
            ),
        ]
    )

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

def create_retriever(
    vector_store: QdrantVectorStore,
    k: int = 4,
) -> VectorStoreRetriever:
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
        },
    )

def create_threshold_retriever(
    vector_store: QdrantVectorStore,
    k: int = 4,
    score_threshold: float = 0.40,
) -> VectorStoreRetriever:
    return vector_store.as_retriever(
        search_type=(
            "similarity_score_threshold"
        ),
        search_kwargs={
            "k": k,
            "score_threshold": score_threshold,
        },
    )

def create_mmr_retriever(
    vector_store: QdrantVectorStore,
    k: int = 4,
    fetch_k: int = 12,
    lambda_mult: float = 0.5,
) -> VectorStoreRetriever:
    if fetch_k < k:
        raise ValueError(
            "fetch_k doit être supérieur "
            "ou égal à k."
        )

    if not 0 <= lambda_mult <= 1:
        raise ValueError(
            "lambda_mult doit être compris "
            "entre 0 et 1."
        )
    
    admission_filter = (
        create_category_filter(
            "admission"
        )
    )


    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult,
            "filter": admission_filter
        },
    )


def retrieve_documents(
    question: str,
    retriever: VectorStoreRetriever,
) -> list[Document]:
    clean_question = question.strip()

    if not clean_question:
        return []

    documents = retriever.invoke(
        clean_question
    )

    return documents
