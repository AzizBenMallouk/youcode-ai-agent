from langchain_core.messages import (
    HumanMessage,
)

from youcode_guide.agents.rescheduling.factory import (
    create_rescheduling_agent,
)
from youcode_guide.agents.rescheduling.models import (
    ReschedulingAgentResponse,
)
from youcode_guide.database.sqlite.connection import (
    create_database_session,
)
from youcode_guide.metier.repositories.visitor_request_repository import (
    VisitorRequestRepository,
)


class ReschedulingAgentService:
    def __init__(self) -> None:
        self.agent = (
            create_rescheduling_agent()
        )

    def invoke(
        self,
        *,
        reference: str,
        session_id: str,
    ) -> ReschedulingAgentResponse:
        instruction = (
            "Traite la demande de report "
            f"portant la référence "
            f"{reference}. "
            "Récupère les prochaines sessions "
            "officielles compatibles. "
            "Si une session est disponible, "
            "enregistre une proposition. "
            "Ne confirme pas définitivement "
            "le report et n'envoie aucun "
            "e-mail."
        )

        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=instruction
                    )
                ]
            },
            config={
                "configurable": {
                    "thread_id": session_id,
                }
            },
        )

        structured_response = result.get(
            "structured_response"
        )

        if isinstance(
            structured_response,
            ReschedulingAgentResponse,
        ):
            return structured_response

        if isinstance(
            structured_response,
            dict,
        ):
            return (
                ReschedulingAgentResponse
                .model_validate(
                    structured_response
                )
            )

        # Ollama ne retourne pas toujours
        # structured_response. La base constitue
        # la source fiable du résultat.
        return self._build_response_from_database(
            reference=reference,
        )

    def _build_response_from_database(
        self,
        *,
        reference: str,
    ) -> ReschedulingAgentResponse:
        session = create_database_session()

        try:
            repository = (
                VisitorRequestRepository(
                    session=session,
                )
            )

            request = (
                repository.find_by_reference(
                    reference
                )
            )

            if request is None:
                return ReschedulingAgentResponse(
                    status="error",
                    answer=(
                        "La demande de report "
                        "est introuvable."
                    ),
                    reference=reference,
                    external_session_id=None,
                    proposed_test_date=None,
                    requires_human=True,
                )

            if (
                request.status
                == "pending_approval"
                and request
                .external_session_id
                and request
                .proposed_test_date
            ):
                return ReschedulingAgentResponse(
                    status="proposed",
                    answer=(
                        "Une nouvelle session "
                        "a été proposée. "
                        "La proposition attend "
                        "une validation humaine."
                    ),
                    reference=(
                        request.reference
                    ),
                    external_session_id=(
                        request
                        .external_session_id
                    ),
                    proposed_test_date=(
                        request
                        .proposed_test_date
                        .isoformat()
                    ),
                    requires_human=True,
                )

            if request.status == "pending_review":
                return ReschedulingAgentResponse(
                    status="no_session",
                    answer=(
                        "Aucune session "
                        "compatible n'est "
                        "actuellement disponible. "
                        "Une intervention humaine "
                        "est nécessaire."
                    ),
                    reference=(
                        request.reference
                    ),
                    external_session_id=None,
                    proposed_test_date=None,
                    requires_human=True,
                )

            if request.status in {
                "confirmed",
                "rejected",
                "cancelled",
            }:
                return ReschedulingAgentResponse(
                    status=(
                        "requires_human"
                    ),
                    answer=(
                        "Cette demande est déjà "
                        "clôturée."
                    ),
                    reference=(
                        request.reference
                    ),
                    external_session_id=(
                        request
                        .external_session_id
                    ),
                    proposed_test_date=(
                        request
                        .proposed_test_date
                        .isoformat()
                        if request
                        .proposed_test_date
                        else None
                    ),
                    requires_human=True,
                )

            return ReschedulingAgentResponse(
                status="requires_human",
                answer=(
                    "La demande n'a pas pu "
                    "être finalisée "
                    "automatiquement."
                ),
                reference=request.reference,
                external_session_id=(
                    request.external_session_id
                ),
                proposed_test_date=(
                    request.proposed_test_date
                    .isoformat()
                    if request.proposed_test_date
                    else None
                ),
                requires_human=True,
            )

        finally:
            session.close()