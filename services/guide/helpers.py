from typing import Any
from shared.rag.retriever import RetrievalResult

def format_documents_for_agent(
    result: RetrievalResult,
) -> dict[str, Any]:
    """
    Transforme un RetrievalResult en données
    simples utilisables par le Guide Agent.

    Les children servent à la recherche, mais
    seuls les parents sont envoyés au LLM.
    """

    if not result.information_available:
        return {
            "status": "INFORMATION_NOT_AVAILABLE",
            "question": result.question,
            "best_score": result.best_score,
            "documents": [],
        }

    formatted_documents: list[dict[str, Any]] = []

    for parent in result.parents:
        formatted_documents.append(
            {
                "content": parent.page_content,
                "source": parent.metadata.get("source"),
                "title": parent.metadata.get("title"),
                "category": parent.metadata.get("category"),
                "score": parent.metadata.get("retrieval_score"),
            }
        )

    return {
        "status": "DOCUMENTS_FOUND",
        "question": result.question,
        "best_score": result.best_score,
        "documents": formatted_documents,
    }
