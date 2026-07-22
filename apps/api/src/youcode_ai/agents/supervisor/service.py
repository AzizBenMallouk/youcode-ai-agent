import logging
from collections.abc import Sequence

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)

from youcode_ai.agents.supervisor.prompt import (
    SUPERVISOR_SYSTEM_PROMPT,
)
from youcode_ai.agents.supervisor.schemas import (
    SupervisorDecision,
)
from youcode_ai.core.config import settings
from youcode_ai.core.llm import (
    create_chat_model,
)


logger = logging.getLogger(__name__)


class SupervisorService:
    def __init__(self) -> None:
        model = create_chat_model()

        self.structured_model = (
            model.with_structured_output(
                SupervisorDecision
            )
        )

    def route(
        self,
        *,
        messages: Sequence[BaseMessage],
    ) -> SupervisorDecision:
        """
        Analyse la conversation et retourne
        uniquement une décision de routage.
        """

        conversation = (
            self._prepare_messages(
                messages
            )
        )

        if not conversation:
            return self._fallback_decision()

        try:
            result = (
                self.structured_model.invoke(
                    [
                        SystemMessage(
                            content=(
                                SUPERVISOR_SYSTEM_PROMPT
                            )
                        ),
                        *conversation,
                    ]
                )
            )

            if isinstance(
                result,
                SupervisorDecision,
            ):
                return result

            logger.error(
                "Supervisor returned an invalid "
                "structured response."
            )

            return self._fallback_decision()

        except Exception:
            logger.exception(
                "Supervisor routing failed."
            )

            return self._fallback_decision()

    @staticmethod
    def _prepare_messages(
        messages: Sequence[BaseMessage],
    ) -> list[BaseMessage]:
        """
        Conserve uniquement les messages utiles
        et limite la taille de l'historique.
        """

        conversation = [
            message
            for message in messages
            if isinstance(
                message,
                (
                    HumanMessage,
                    AIMessage,
                ),
            )
        ]

        max_messages = (
            settings.max_history_messages
        )

        if max_messages <= 0:
            return conversation

        return conversation[
            -max_messages:
        ]

    @staticmethod
    def _fallback_decision(
    ) -> SupervisorDecision:
        """
        Décision sûre utilisée lorsque le modèle
        ne peut pas classifier le message.
        """

        return SupervisorDecision(
            route="clarification",
            language="fr",
            clarification_question=(
                "Pouvez-vous préciser votre "
                "demande concernant YouCode ?"
            ),
        )


def create_supervisor_service(
) -> SupervisorService:
    return SupervisorService()