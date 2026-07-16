from langchain_core.tools import (
    BaseTool,
    tool,
)

from youcode_guide.rag.service import (
    RAGService,
)


def create_knowledge_tool(
    rag_service: RAGService,
) -> BaseTool:
    @tool
    def search_youcode_knowledge(
        question: str,
    ) -> dict:
        """
        Recherche exclusivement dans les documents officiels
        de YouCode.

        Utiliser ce tool pour toute question factuelle sur :
        présentation, formations, programmes, admissions,
        campus, pédagogie, carrières, événements et
        informations pratiques.

        Ne pas utiliser ce tool pour modifier ou consulter
        un dossier personnel.
        """
        result = rag_service.ask(question)

        return result.model_dump(
            mode="json"
        )

    return search_youcode_knowledge