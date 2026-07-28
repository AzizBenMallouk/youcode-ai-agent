import logging
from typing import Any

from langchain_core.messages import (
    AIMessage,
)
from .service import (
    SupervisorService,
)
from ..state import (
    OrchestratorState,
)

logger = logging.getLogger(__name__)


class SupervisorNodes:
    def __init__(
        self,
        service: SupervisorService,
    ) -> None:
        self.service = service

    def route_message(
        self,
        state: OrchestratorState,
    ) -> dict[str, Any]:
        """
        Sélectionne le workflow qui doit traiter
        le dernier message du visiteur.
        """

        messages = state.get(
            "messages",
            [],
        )

        decision = self.service.route(messages=messages)

        update: dict[str, Any] = {
            "route": decision.route,
        }

        if decision.route == "clarification":
            question = decision.clarification_question or self._default_clarification(
                decision.language
            )

            update["final_response"] = {
                "status": "clarification",
                "language": decision.language,
                "answer": question,
                "requires_human": False,
            }

        return update

    def clarification(
        self,
        state: OrchestratorState,
    ) -> dict[str, Any]:
        """
        Retourne la question de clarification
        préparée par le Supervisor.
        """

        response = state.get("final_response") or {}

        language = str(
            response.get(
                "language",
                "fr",
            )
        )

        answer = str(
            response.get(
                "answer",
                self._default_clarification(language),
            )
        )

        final_response = {
            "status": "clarification",
            "language": language,
            "answer": answer,
            "requires_human": False,
        }

        return {
            "requires_human": False,
            "messages": [AIMessage(content=answer)],
            "final_response": final_response,
        }

    def out_of_scope(
        self,
        state: OrchestratorState,
    ) -> dict[str, Any]:
        """
        Répond aux demandes sans rapport avec
        YouCode.
        """

        language = self._detect_response_language(state)

        answer = self._out_of_scope_answer(language)

        return {
            "requires_human": False,
            "messages": [AIMessage(content=answer)],
            "final_response": {
                "status": "out_of_scope",
                "language": language,
                "answer": answer,
                "requires_human": False,
            },
        }

    @staticmethod
    def _detect_response_language(
        state: OrchestratorState,
    ) -> str:
        # Fallback language (Orchestrator doesn't track support_draft)
        # We could potentially extract language from state if we added it, but for now fallback to fr.
        return "fr"

    @staticmethod
    def _default_clarification(
        language: str,
    ) -> str:
        questions = {
            "fr": ("Pouvez-vous préciser votre demande concernant YouCode ?"),
            "en": ("Could you clarify your request about YouCode?"),
            "ar": ("هل يمكنك توضيح طلبك المتعلق بـ YouCode؟"),
            "darija": ("واش تقدر توضح ليا الطلب ديالك على YouCode؟"),
        }

        return questions.get(
            language,
            questions["fr"],
        )

    @staticmethod
    def _out_of_scope_answer(
        language: str,
    ) -> str:
        answers = {
            "fr": ("Je peux uniquement vous aider concernant YouCode."),
            "en": ("I can only help you with questions about YouCode."),
            "ar": ("يمكنني مساعدتك فقط في الأسئلة المتعلقة بـ YouCode."),
            "darija": ("نقدر نعاونك غير فالحوايج اللي عندها علاقة بـ YouCode."),
        }

        return answers.get(
            language,
            answers["fr"],
        )


def create_supervisor_nodes() -> SupervisorNodes:
    return SupervisorNodes(service=SupervisorService())
