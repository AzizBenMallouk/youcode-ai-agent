from langchain_core.tools import tool

from youcode_guide.metier.retriever.retriever import ParentChildRetriever
from youcode_guide.metier.retriever.document_formatter import (
    format_documents_for_agent,
)
from youcode_guide.metier.models.knowledge_search_result import KnowledgeSearchResult
from youcode_guide.metier.enums.knowledge_search_status import KnowledgeSearchStatus


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

        cleaned_query = query.strip()

        if not cleaned_query:
            result = KnowledgeSearchResult(
                status=KnowledgeSearchStatus.NOT_FOUND,
                query="",
                message=(
                    "La requête de recherche est vide."
                ),
            )

            return result.model_dump_json()

        try:
            retrieval_result = retriever.invoke(
                cleaned_query,
            )

            # print(retrieval_result)

        except Exception:
            result = KnowledgeSearchResult(
                status=(
                    KnowledgeSearchStatus.TECHNICAL_ERROR
                ),
                query=cleaned_query,
                message=(
                    "La recherche documentaire est "
                    "temporairement indisponible."
                ),
            )

            return result.model_dump_json()
        
        if not retrieval_result.information_available:
            result = KnowledgeSearchResult(
                status=KnowledgeSearchStatus.NOT_FOUND,
                query=cleaned_query,
                document_count=0,
                context="",
                message=(
                    "Aucun document officiel suffisamment "
                    "pertinent n'a été trouvé."
                ),
            )

            return result.model_dump_json()

        context = format_documents_for_agent(
            retrieval_result,
        )

        result = KnowledgeSearchResult(
            status=KnowledgeSearchStatus.FOUND,
            query=cleaned_query,
            document_count=(
                retrieval_result.parent_count
            ),
            context=context,
            message=(
                "Des documents officiels pertinents "
                "ont été trouvés."
            ),
        )

        return result.model_dump_json()


    return search_youcode_knowledge