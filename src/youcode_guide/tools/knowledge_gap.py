import logging
from typing import Literal

from langchain_core.tools import tool

from youcode_guide.knowledge.service import (
    KnowledgeGapService,
)
from youcode_guide.tools.utils import (
    tool_response,
)


logger = logging.getLogger(__name__)


SupportedLanguage = Literal[
    "fr",
    "en",
    "ar",
    "darija",
]


SupportedCategory = Literal[
    "general",
    "admission",
    "program",
    "campus",
    "pedagogy",
    "career",
    "event",
    "practical",
]


def create_report_knowledge_gap_tool(
    service: KnowledgeGapService,
):
    @tool
    def report_knowledge_gap(
        question: str,
        language: SupportedLanguage,
        category: SupportedCategory,
    ) -> str:
        """
        Signale une information officielle manquante concernant YouCode.

        Utilise cet outil lorsque :
        - search_youcode_knowledge retourne status="not_found" ;
        - ou search_youcode_knowledge retourne status="found", mais les
        documents ne contiennent pas explicitement la réponse demandée.

        La présence de documents liés à YouCode ne signifie pas que
        l'information demandée est disponible.

        Ne l'utilise pas pour :
        - une question hors sujet ;
        - une question ambiguë ;
        - une erreur technique ;
        - une demande personnelle traitée par un autre tool ;
        - une question dont la réponse est explicitement présente dans
        le contexte documentaire.

        La question doit être autonome, claire et ne doit contenir aucune
        donnée personnelle inutile.
        """

        cleaned_question = question.strip()

        if not cleaned_question:
            return tool_response(
                {
                    "success": False,
                    "status": "invalid_question",
                    "message": (
                        "La question à signaler "
                        "est vide."
                    ),
                }
            )

        try:
            result = service.report(
                question=cleaned_question,
                language=language,
                category=category,
            )

        except ValueError as error:
            logger.warning(
                "Invalid knowledge gap: %s",
                error,
            )

            return tool_response(
                {
                    "success": False,
                    "status": "invalid_question",
                    "message": (
                        "La question ne peut pas "
                        "être signalée."
                    ),
                }
            )

        except Exception:
            logger.exception(
                "Knowledge gap reporting failed."
            )

            return tool_response(
                {
                    "success": False,
                    "status": "technical_error",
                    "message": (
                        "Le signalement n'a pas pu "
                        "être enregistré."
                    ),
                }
            )

        return tool_response(
            {
                "success": True,
                "status": "reported",
                "gap_id": result.gap.id,
                "match_type": (
                    result.match_type.value
                ),
                "occurrence_count": (
                    result.gap.occurrence_count
                ),
                "message": (
                    "La question a été enregistrée "
                    "pour vérification."
                ),
            }
        )

    return report_knowledge_gap