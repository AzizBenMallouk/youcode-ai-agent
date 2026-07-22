from functools import lru_cache
from typing import Any
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from youcode_ai.api.schemas.chat import (
    ChatErrorResponse,
    ChatRequest,
    ChatResponse,
)
from youcode_ai.orchestration.service import (
    YouCodeOrchestrationService,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@lru_cache(maxsize=1)
def get_orchestration_service(
) -> YouCodeOrchestrationService:
    return YouCodeOrchestrationService()


@router.post(
    "/messages",
    response_model=ChatResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ChatErrorResponse,
        }
    },
)
def send_message(
    payload: ChatRequest,
    service: YouCodeOrchestrationService = (
        Depends(
            get_orchestration_service
        )
    ),
) -> ChatResponse:
    """
    Envoie un message au système multi-agent.

    Si session_id est absent, une nouvelle
    conversation est créée.
    """

    session_id = (
        payload.session_id
        or str(uuid4())
    )

    try:
        result = service.invoke(
            session_id=session_id,
            message=payload.message,
        )

        state = service.get_state(
            session_id=session_id
        )

        agent = _resolve_agent(
            result=result,
            state=state,
        )

        standard_fields = {
            "status",
            "language",
            "answer",
            "requires_human",
        }

        additional_data: dict[
            str,
            Any,
        ] = {
            key: value
            for key, value in result.items()
            if (
                key not in standard_fields
                and value is not None
            )
        }

        return ChatResponse(
            session_id=session_id,
            agent=agent,
            status=str(
                result.get(
                    "status",
                    "answered",
                )
            ),
            language=_safe_language(
                result.get("language")
            ),
            answer=str(
                result.get(
                    "answer",
                    "Réponse indisponible.",
                )
            ),
            requires_human=bool(
                result.get(
                    "requires_human",
                    False,
                )
            ),
            data=additional_data,
        )

    except Exception as error:
        raise HTTPException(
            status_code=(
                status
                .HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to process the message."
            ),
        ) from error


def _resolve_agent(
    *,
    result: dict[str, Any],
    state: dict[str, Any],
) -> str:
    """
    Détermine quel agent a produit la réponse.
    """

    response_status = result.get(
        "status"
    )

    if response_status in {
        "clarification",
        "out_of_scope",
    }:
        return "supervisor"

    active_agent = state.get(
        "active_agent"
    )

    if active_agent in {
        "guide",
        "support",
        "newsletter",
    }:
        return active_agent

    return "supervisor"


def _safe_language(
    value: object,
) -> str:
    language = str(
        value or "fr"
    )

    if language in {
        "fr",
        "en",
        "ar",
        "darija",
    }:
        return language

    return "fr"