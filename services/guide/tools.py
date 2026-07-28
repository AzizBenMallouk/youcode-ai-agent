import logging
from typing import (
    Any,
    Literal,
)

from langchain_core.tools import (
    BaseTool,
    tool,
)
from shared.application.services.factories import (
    create_registration_service,
)
from shared.application.services.registration import (
    RegistrationService,
)
from shared.rag.retriever import (
    ParentChildRetriever,
    RetrievalResult,
    create_parent_child_retriever,
)

logger = logging.getLogger(__name__)


# -------------------------------------
# Formatage des documents RAG
# -------------------------------------


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
            "status": ("INFORMATION_NOT_AVAILABLE"),
            "question": result.question,
            "best_score": result.best_score,
            "documents": [],
        }

    formatted_documents: list[dict[str, Any]] = []

    for parent in result.parents:
        formatted_documents.append(
            {
                "content": (parent.page_content),
                "source": (parent.metadata.get("source")),
                "title": (parent.metadata.get("title")),
                "category": (parent.metadata.get("category")),
                "score": (parent.metadata.get("retrieval_score")),
            }
        )

    return {
        "status": "DOCUMENTS_FOUND",
        "question": result.question,
        "best_score": result.best_score,
        "documents": formatted_documents,
    }


# -------------------------------------
# Tool RAG
# -------------------------------------


def create_search_youcode_knowledge_tool(
    *,
    retriever: ParentChildRetriever,
) -> BaseTool:
    @tool("search_youcode_knowledge")
    def search_youcode_knowledge(
        question: str,
    ) -> dict[str, Any]:
        """
        Search the official YouCode knowledge
        base for stable factual information.

        Use this tool for questions about YouCode,
        its programs, campuses, pedagogy, careers,
        events and practical information.

        Do not use this tool as the primary source
        for dynamic registration dates or the
        current registration status.

        The tool returns official documents, not
        a final answer.
        """

        normalized_question = question.strip()

        if not normalized_question:
            return {
                "status": ("INFORMATION_NOT_AVAILABLE"),
                "question": question,
                "best_score": None,
                "documents": [],
            }

        try:
            result = retriever.retrieve(normalized_question)

            return format_documents_for_agent(result)

        except Exception:
            logger.exception("YouCode knowledge search failed.")

            return {
                "status": "SEARCH_UNAVAILABLE",
                "question": (normalized_question),
                "best_score": None,
                "documents": [],
            }

    return search_youcode_knowledge


# -------------------------------------
# Tool Registration API
# -------------------------------------


def create_registration_status_tool(
    *,
    registration_service: (RegistrationService),
) -> BaseTool:
    @tool("get_registration_status")
    def get_registration_status(
        program: Literal[
            "full_program",
            "bootcamp",
        ] = "full_program",
        campus: Literal[
            "Safi",
            "Youssoufia",
            "Nador",
        ]
        | None = None,
    ) -> dict[str, Any]:
        """
        Get dynamic official YouCode registration
        information.

        Use this tool for questions about:
        - whether registrations are currently open;
        - registration opening or closing dates;
        - current registration links;
        - available places;
        - registration status by campus.

        The tool returns structured official data,
        not a final answer.
        """

        try:
            result = registration_service.get_status(
                program=program,
                campus=campus,
            )

        except ValueError:
            logger.warning(
                "Invalid registration query: program=%s campus=%s.",
                program,
                campus,
            )

            return {
                "status": ("INVALID_REGISTRATION_QUERY"),
                "program": program,
                "campus": campus,
            }

        except Exception:
            logger.exception("Registration lookup failed.")

            return {
                "status": ("REGISTRATION_SERVICE_UNAVAILABLE"),
                "program": program,
                "campus": campus,
            }

        if not result.service_available:
            return {
                "status": ("REGISTRATION_SERVICE_UNAVAILABLE"),
                "program": result.program,
                "campus": result.campus,
            }

        if not result.information_available:
            return {
                "status": ("REGISTRATION_INFORMATION_NOT_AVAILABLE"),
                "program": result.program,
                "campus": result.campus,
            }

        return {
            "status": ("REGISTRATION_DATA_FOUND"),
            "program": result.program,
            "campus": result.campus,
            "registration_status": (result.status),
            "opening_date": (
                result.opening_date.isoformat() if result.opening_date else None
            ),
            "closing_date": (
                result.closing_date.isoformat() if result.closing_date else None
            ),
            "registration_url": (result.registration_url),
            "available_places": (result.available_places),
            "message": result.message,
            "updated_at": (
                result.updated_at.isoformat() if result.updated_at else None
            ),
        }

    return get_registration_status


# -------------------------------------
# Factory des tools du Guide
# -------------------------------------


def create_guide_tools() -> list[BaseTool]:
    retriever = create_parent_child_retriever()

    registration_service = create_registration_service()

    return [
        create_search_youcode_knowledge_tool(retriever=retriever),
        create_registration_status_tool(registration_service=(registration_service)),
    ]
