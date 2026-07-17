from langchain_core.tools import tool

from youcode_guide.rag.retriever import ParentChildRetriever
from youcode_guide.rag.document_formatter import (
    format_documents_for_agent,
)


def create_knowledge_tool(
    retriever: ParentChildRetriever,
):
    @tool
    def search_youcode_knowledge(
        query: str,
    ) -> str:
        """
        Recherche des informations dans les documents officiels
        de YouCode.

        Utilise obligatoirement cet outil pour toute question
        factuelle concernant YouCode : présentation, admissions,
        formations, campus, pédagogie, débouchés, événements,
        inscriptions et informations pratiques.

        La requête doit être autonome. Elle ne doit pas contenir
        de références ambiguës comme « ce campus » ou « cette
        formation ».
        """

        documents = retriever.invoke(query)

        return format_documents_for_agent(
            documents,
        )

    return search_youcode_knowledge