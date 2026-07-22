import logging
from collections.abc import Sequence

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
)

from youcode_ai.agents.guide.agent import (
    create_guide_agent,
)
from youcode_ai.agents.guide.schemas import (
    GuideResponse,
)
from youcode_ai.domain.enums.common import (
    Language,
)



class GuideAgentService:
    def __init__(self) -> None:
        self.agent = create_guide_agent()

    def invoke(
        self,
        *,
        message: str,
        history: Sequence[
            BaseMessage
        ] | None = None,
    ) -> GuideResponse:
        """
        Exécute le Guide Agent.

        L'historique est fourni par le workflow
        principal. Le service ne conserve aucun
        état en mémoire.
        """

        messages: list[BaseMessage] = list(
            history or []
        )

        messages.append(
            HumanMessage(
                content=message.strip()
            )
        )

        try:
            result = self.agent.invoke(
                {
                    "messages": messages,
                }
            )

            response = result.get(
                "structured_response"
            )

            if isinstance(
                response,
                GuideResponse,
            ):
                return response


            return self._technical_error()

        except Exception:
            return self._technical_error()

    @staticmethod
    def _technical_error() -> GuideResponse:
        return GuideResponse(
            language=Language.FR,
            category="practical",
            answer=(
                "Une erreur technique est "
                "survenue pendant la recherche. "
                "Veuillez réessayer."
            ),
            information_available=False,
            requires_human=False,
        )


def create_guide_agent_service(
) -> GuideAgentService:
    return GuideAgentService()