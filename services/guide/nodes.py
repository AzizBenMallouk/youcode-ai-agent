from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from .service import GuideAgentService
from .state import GuideState
from shared.core.config import settings


class GuideNodes:
    def __init__(
        self,
        service: GuideAgentService,
    ) -> None:
        self.service = service

    def answer_question(
        self,
        state: GuideState,
    ) -> dict[str, Any]:
        """
        Répond à la dernière question du
        visiteur avec le Guide Agent.
        """

        messages = state.get(
            "messages",
            [],
        )

        user_message = self._get_last_user_message(messages)

        if not user_message:
            return self._missing_message()

        # On ne transmet pas le dernier
        # HumanMessage dans history car le
        # service l'ajoute lui-même.
        history = self._history_before_last_user_message(messages)

        try:
            response = self.service.invoke(
                message=user_message,
                history=history,
            )

            response_data = response.model_dump(mode="json")

            return {
                "messages": [AIMessage(content=response.answer)]
            }

        except Exception:
            import traceback

            traceback.print_exc()
            return self._technical_error()

    @staticmethod
    def _get_last_user_message(
        messages: list[BaseMessage],
    ) -> str | None:
        """
        Récupère le dernier message humain.
        """

        for message in reversed(messages):
            if not isinstance(
                message,
                HumanMessage,
            ):
                continue

            content = message.content

            if isinstance(content, str):
                content = content.strip()

                if content:
                    return content

        return None

    @staticmethod
    def _history_before_last_user_message(
        messages: list[BaseMessage],
    ) -> list[BaseMessage]:
        """
        Retourne l'historique sans le dernier
        message humain.

        Le GuideAgentService ajoutera lui-même
        ce dernier message.
        """

        last_user_index: int | None = None

        for index in range(
            len(messages) - 1,
            -1,
            -1,
        ):
            if isinstance(
                messages[index],
                HumanMessage,
            ):
                last_user_index = index
                break

        if last_user_index is None:
            history = list(messages)
        else:
            history = list(messages[:last_user_index])
            
        max_messages = settings.max_history_messages
        if max_messages > 0:
            return history[-max_messages:]
        return history

    @staticmethod
    def _missing_message() -> dict[str, Any]:
        answer = "Veuillez écrire une question concernant YouCode."

        return {
            "messages": [AIMessage(content=answer)],
        }

    @staticmethod
    def _technical_error() -> dict[str, Any]:
        answer = (
            "Une erreur technique est "
            "survenue pendant la recherche. "
            "Veuillez réessayer."
        )

        return {
            "messages": [AIMessage(content=answer)],
        }


def create_guide_nodes() -> GuideNodes:
    return GuideNodes(service=GuideAgentService())
