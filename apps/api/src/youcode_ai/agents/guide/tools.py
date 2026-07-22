import logging

from typing import Any

from langchain_core.tools import (
    BaseTool,
    tool,
)

from youcode_ai.rag.retriever import (
    ParentChildRetriever,
    RetrievalResult,
    create_parent_child_retriever,
)


logger = logging.getLogger(__name__)


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
            "status": (
                "INFORMATION_NOT_AVAILABLE"
            ),
            "question": result.question,
            "best_score": (
                result.best_score
            ),
            "documents": [],
        }

    formatted_documents: list[
        dict[str, Any]
    ] = []

    for parent in result.parents:
        formatted_documents.append(
            {
                "content": (
                    parent.page_content
                ),
                "source": (
                    parent.metadata.get(
                        "source"
                    )
                ),
                "title": (
                    parent.metadata.get(
                        "title"
                    )
                ),
                "category": (
                    parent.metadata.get(
                        "category"
                    )
                ),
                "score": (
                    parent.metadata.get(
                        "retrieval_score"
                    )
                ),
            }
        )

    return {
        "status": "DOCUMENTS_FOUND",
        "question": result.question,
        "best_score": result.best_score,
        "documents": formatted_documents,
    }


def create_search_youcode_knowledge_tool(
    *,
    retriever: ParentChildRetriever,
) -> BaseTool:
    @tool(
        "search_youcode_knowledge"
    )
    def search_youcode_knowledge(
        question: str,
    ) -> dict[str, Any]:
        """
        Search the official YouCode knowledge
        base for factual information.

        Use this tool for questions about YouCode,
        its programs, admissions, campuses,
        pedagogy, careers, events and practical
        information.

        The tool returns official documents, not
        a final answer.
        """

        normalized_question = (
            question.strip()
        )

        if not normalized_question:
            return {
                "status": (
                    "INFORMATION_NOT_AVAILABLE"
                ),
                "question": question,
                "best_score": None,
                "documents": [],
            }

        try:
            result = retriever.retrieve(
                normalized_question
            )

            return (
                format_documents_for_agent(
                    result
                )
            )

        except Exception:
            logger.exception(
                "YouCode knowledge search "
                "failed."
            )

            return {
                "status": "SEARCH_UNAVAILABLE",
                "question": (
                    normalized_question
                ),
                "best_score": None,
                "documents": [],
            }

    return search_youcode_knowledge


def create_guide_tools(
) -> list[BaseTool]:
    retriever = (
        create_parent_child_retriever()
    )

    return [
        create_search_youcode_knowledge_tool(
            retriever=retriever
        )
    ]