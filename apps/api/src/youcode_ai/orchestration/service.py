import logging
from typing import Any

from langchain_core.messages import (
    HumanMessage,
)

from youcode_ai.orchestration.graph import (
    create_youcode_graph,
)


logger = logging.getLogger(__name__)


class YouCodeOrchestrationService:
    def __init__(self) -> None:
        self.graph = create_youcode_graph()

    def invoke(
        self,
        *,
        session_id: str,
        message: str,
    ) -> dict[str, Any]:
        """
        Envoie un nouveau message dans le graph.

        Le thread_id permet au checkpointer
        LangGraph de retrouver le state de cette
        conversation.
        """

        clean_session_id = (
            session_id.strip()
        )

        clean_message = message.strip()

        if not clean_session_id:
            raise ValueError(
                "session_id is required."
            )

        if not clean_message:
            return {
                "status": "invalid_message",
                "language": "fr",
                "answer": (
                    "Veuillez écrire un message."
                ),
                "requires_human": False,
            }

        try:
            result = self.graph.invoke(
                {
                    "session_id": (
                        clean_session_id
                    ),
                    "messages": [
                        HumanMessage(
                            content=clean_message
                        )
                    ],

                    # Réinitialisation des champs
                    # propres à ce nouveau tour.
                    "final_response": None,
                    "requires_human": False,
                },
                config={
                    "configurable": {
                        "thread_id": (
                            clean_session_id
                        ),
                    }
                },
            )

            final_response = result.get(
                "final_response"
            )

            if isinstance(
                final_response,
                dict,
            ):
                return final_response

            logger.error(
                "Graph returned no valid final "
                "response for session %s.",
                clean_session_id,
            )

            return self._technical_error()

        except Exception:
            logger.exception(
                "Graph execution failed for "
                "session %s.",
                clean_session_id,
            )

            return self._technical_error()

    def get_state(
        self,
        *,
        session_id: str,
    ) -> dict[str, Any]:
        """
        Retourne le state actuel d'une
        conversation.

        À utiliser uniquement pour les tests ou
        l'administration, jamais directement
        dans la réponse visiteur.
        """

        snapshot = self.graph.get_state(
            {
                "configurable": {
                    "thread_id": session_id,
                }
            }
        )

        return dict(
            snapshot.values or {}
        )

    @staticmethod
    def _technical_error(
    ) -> dict[str, Any]:
        return {
            "status": "error",
            "language": "fr",
            "answer": (
                "Une erreur technique est "
                "survenue. Veuillez réessayer."
            ),
            "requires_human": False,
        }


def create_orchestration_service(
) -> YouCodeOrchestrationService:
    return YouCodeOrchestrationService()