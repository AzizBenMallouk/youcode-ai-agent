from datetime import date

from langchain.tools import (
    ToolRuntime,
    tool,
)
from langchain_core.tools import BaseTool

from youcode_guide.agents.shared.context import (
    AgentRuntimeContext,
)
from youcode_guide.metier.enums.consent_purpose import (
    ConsentPurpose,
)
from youcode_guide.metier.enums.language import Language
from youcode_guide.metier.models.test_reschedule_request import (
    TestRescheduleRequest,
)
from youcode_guide.metier.services.visitor_request_service import (
    VisitorRequestService,
)


def create_test_reschedule_tool(
    service: VisitorRequestService,
) -> BaseTool:
    @tool
    def create_test_reschedule_request(
        email: str,
        language: Language,
        scheduled_test_date: date,
        requested_test_date: date | None,
        description: str | None,
        runtime: ToolRuntime[
            AgentRuntimeContext
        ],
    ) -> dict:
        """
        Enregistre une demande de report d'un test
        présentiel YouCode.

        Utiliser uniquement après avoir obtenu :
        - l'email de candidature ;
        - la date actuellement prévue ;
        - le consentement explicite.

        Ce tool enregistre seulement une demande.
        Il ne confirme jamais que le report est accepté.
        """
        purpose = (
            ConsentPurpose.TEST_RESCHEDULE.value
        )

        token = (
            runtime.context
            .get_consent_token(purpose)
        )

        if token is None:
            return {
                "success": False,
                "error_code": (
                    "consent_required"
                ),
                "consent_purpose": purpose,
                "message": (
                    "Un consentement explicite "
                    "est nécessaire."
                ),
            }

        try:
            result = (
                service.create_test_reschedule(
                    TestRescheduleRequest(
                        session_id=(
                            runtime
                            .context
                            .session_id
                        ),
                        email=email,
                        language=language,
                        scheduled_test_date=(
                            scheduled_test_date
                        ),
                        requested_test_date=(
                            requested_test_date
                        ),
                        description=description,
                        consent_token=token,
                    )
                )
            )

            return {
                "success": True,
                "request": result.model_dump(
                    mode="json"
                ),
            }

        except ValueError as error:
            return {
                "success": False,
                "error_code": (
                    "request_rejected"
                ),
                "message": str(error),
            }

    return create_test_reschedule_request