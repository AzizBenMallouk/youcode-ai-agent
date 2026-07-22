import logging
from typing import Any

from langchain_core.messages import (
    AIMessage,
)

from youcode_ai.agents.supervisor.service import (
    SupervisorService,
)
from youcode_ai.orchestration.state import (
    YouCodeState,
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
        state: YouCodeState,
    ) -> dict[str, Any]:
        """
        Sélectionne le workflow qui doit traiter
        le dernier message du visiteur.
        """

        continuation_route = (
            self._get_continuation_route(
                state
            )
        )

        if continuation_route is not None:
            return {
                "route": continuation_route,
            }

        messages = state.get(
            "messages",
            [],
        )

        decision = self.service.route(
            messages=messages
        )

        update: dict[str, Any] = {
            "route": decision.route,
        }

        if decision.route == "clarification":
            question = (
                decision.clarification_question
                or self._default_clarification(
                    decision.language
                )
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
        state: YouCodeState,
    ) -> dict[str, Any]:
        """
        Retourne la question de clarification
        préparée par le Supervisor.
        """

        response = state.get(
            "final_response"
        ) or {}

        language = str(
            response.get(
                "language",
                "fr",
            )
        )

        answer = str(
            response.get(
                "answer",
                self._default_clarification(
                    language
                ),
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
            "messages": [
                AIMessage(
                    content=answer
                )
            ],
            "final_response": final_response,
        }

    def out_of_scope(
        self,
        state: YouCodeState,
    ) -> dict[str, Any]:
        """
        Répond aux demandes sans rapport avec
        YouCode.
        """

        language = self._detect_response_language(
            state
        )

        answer = self._out_of_scope_answer(
            language
        )

        return {
            "requires_human": False,
            "messages": [
                AIMessage(
                    content=answer
                )
            ],
            "final_response": {
                "status": "out_of_scope",
                "language": language,
                "answer": answer,
                "requires_human": False,
            },
        }

    @staticmethod
    def _get_continuation_route(
        state: YouCodeState,
    ) -> str | None:
        """
        Empêche le Supervisor de reclassifier
        les réponses courtes d'un workflow actif.
        """

        active_agent = state.get(
            "active_agent"
        )

        if active_agent == "support":
            support_phase = state.get(
                "support_phase"
            )

            terminal_phases = {
                "completed",
                "cancelled",
            }

            if (
                support_phase
                and support_phase
                not in terminal_phases
            ):
                return "support"

        # La continuité Newsletter sera ajoutée
        # lorsque newsletter_phase existera dans
        # le state.
        if active_agent == "newsletter":
            newsletter_phase = state.get(
                "newsletter_phase"
            )

            terminal_phases = {
                "completed",
                "cancelled",
            }

            if (
                newsletter_phase
                and newsletter_phase
                not in terminal_phases
            ):
                return "newsletter"

        return None

    @staticmethod
    def _detect_response_language(
        state: YouCodeState,
    ) -> str:
        """
        Utilise la langue déjà identifiée dans
        le brouillon Support si disponible.
        """

        support_draft = state.get(
            "support_draft",
            {},
        )

        language = support_draft.get(
            "language"
        )

        if language in {
            "fr",
            "en",
            "ar",
            "darija",
        }:
            return language

        return "fr"

    @staticmethod
    def _default_clarification(
        language: str,
    ) -> str:
        questions = {
            "fr": (
                "Pouvez-vous préciser votre "
                "demande concernant YouCode ?"
            ),
            "en": (
                "Could you clarify your request "
                "about YouCode?"
            ),
            "ar": (
                "هل يمكنك توضيح طلبك المتعلق "
                "بـ YouCode؟"
            ),
            "darija": (
                "واش تقدر توضح ليا الطلب ديالك "
                "على YouCode؟"
            ),
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
            "fr": (
                "Je peux uniquement vous aider "
                "concernant YouCode."
            ),
            "en": (
                "I can only help you with "
                "questions about YouCode."
            ),
            "ar": (
                "يمكنني مساعدتك فقط في الأسئلة "
                "المتعلقة بـ YouCode."
            ),
            "darija": (
                "نقدر نعاونك غير فالحوايج اللي "
                "عندها علاقة بـ YouCode."
            ),
        }

        return answers.get(
            language,
            answers["fr"],
        )


def create_supervisor_nodes(
) -> SupervisorNodes:
    return SupervisorNodes(
        service=SupervisorService()
    )