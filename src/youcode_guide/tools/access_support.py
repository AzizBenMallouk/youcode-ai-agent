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
    AccessSupportRequest,
)
from youcode_guide.visitor_requests.service import (
    VisitorRequestService,
)


def create_access_support_tool(
    service: VisitorRequestService,
) -> BaseTool:
    @tool
    def create_access_support_request(
        email: str,
        language: Language,
        description: str,
        platform: str | None,
        runtime: ToolRuntime[
            AgentRuntimeContext
        ],
    ) -> dict:
        """
        Enregistre un problème personnel d'accès ou de
        connexion à une plateforme YouCode.

        Utiliser uniquement après avoir obtenu l'email,
        une description courte et un consentement explicite.

        Ne jamais demander ni accepter un mot de passe,
        un code de connexion ou un code de vérification.
        """
        purpose = (
            ConsentPurpose.ACCESS_SUPPORT.value
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
                service.create_access_support(
                    AccessSupportRequest(
                        session_id=(
                            runtime
                            .context
                            .session_id
                        ),
                        email=email,
                        language=language,
                        description=description,
                        platform=platform,
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

    return create_access_support_request