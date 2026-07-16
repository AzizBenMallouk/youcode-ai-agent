from langchain.tools import (
    ToolRuntime,
    tool,
)
from langchain_core.tools import BaseTool

from youcode_guide.agent.context import (
    AgentRuntimeContext,
)
from youcode_guide.consent.models import (
    ConsentPurpose,
)
from youcode_guide.models import Language
from youcode_guide.visitor_requests.models import (
    WaitlistRequest,
)
from youcode_guide.visitor_requests.service import (
    VisitorRequestService,
)


def create_waitlist_tool(
    service: VisitorRequestService,
) -> BaseTool:
    @tool
    def create_waitlist_request(
        email: str,
        language: Language,
        campus: str | None,
        runtime: ToolRuntime[
            AgentRuntimeContext
        ],
    ) -> dict:
        """
        Enregistre un visiteur sur la liste d'attente
        lorsque les inscriptions ne sont pas ouvertes.

        Utiliser seulement après :
        1. avoir vérifié le statut des inscriptions ;
        2. avoir informé le visiteur de la finalité ;
        3. avoir obtenu son email ;
        4. avoir obtenu son consentement explicite.

        Ne jamais utiliser si les inscriptions sont ouvertes.
        """
        purpose = (
            ConsentPurpose
            .WAITLIST_NOTIFICATION
            .value
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
            result = service.create_waitlist(
                WaitlistRequest(
                    session_id=(
                        runtime.context.session_id
                    ),
                    email=email,
                    language=language,
                    campus=campus,
                    consent_token=token,
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

    return create_waitlist_request