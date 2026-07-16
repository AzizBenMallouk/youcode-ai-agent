from langchain_core.tools import (
    BaseTool,
    tool,
)

from youcode_guide.registration.service import (
    RegistrationService,
)


def create_registration_tool(
    service: RegistrationService,
) -> BaseTool:
    @tool
    def get_registration_status() -> dict:
        """
        Retourne le statut administratif actuel et officiel
        des inscriptions YouCode.

        Toujours utiliser ce tool avant d'affirmer que les
        inscriptions sont ouvertes, fermées ou programmées.
        """
        result = service.get_current_status()

        return result.model_dump(
            mode="json"
        )

    return get_registration_status