import json

from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ToolMessage,
)

from youcode_ai.agents.support.agent import (
    create_support_agent,
)
from youcode_ai.agents.support.context import (
    SupportAgentContext,
)
from youcode_ai.agents.support.schemas import (
    SupportAgentResponse,
)


class SupportAgentService:
    def __init__(self) -> None:
        self.agent = create_support_agent()

    def invoke(
        self,
        *,
        messages: list[BaseMessage],
        session_id: str,
        consent_confirmed: bool,
    ) -> SupportAgentResponse:
        result = self.agent.invoke(
            {
                "messages": messages,
            },
            context=SupportAgentContext(
                session_id=session_id,
                consent_confirmed=(
                    consent_confirmed
                ),
            ),
        )

        result_messages = result.get(
            "messages",
            [],
        )

        answer = self._extract_answer(
            result_messages
        )

        tool_results = (
            self._extract_tool_results(
                result_messages
            )
        )

        return self._build_response(
            answer=answer,
            tool_results=tool_results,
        )

    @staticmethod
    def _extract_answer(
        messages: list[BaseMessage],
    ) -> str:
        for message in reversed(messages):
            if not isinstance(
                message,
                AIMessage,
            ):
                continue

            if not message.content:
                continue

            if isinstance(
                message.content,
                str,
            ):
                return message.content.strip()

            return str(
                message.content
            ).strip()

        return (
            "Je n’ai pas pu préparer une "
            "réponse. Veuillez réessayer."
        )

    @staticmethod
    def _extract_tool_results(
        messages: list[BaseMessage],
    ) -> list[dict[str, Any]]:
        results: list[
            dict[str, Any]
        ] = []

        for message in messages:
            if not isinstance(
                message,
                ToolMessage,
            ):
                continue

            content = message.content

            if isinstance(content, dict):
                results.append(content)
                continue

            if not isinstance(content, str):
                continue

            try:
                parsed = json.loads(
                    content
                )
            except json.JSONDecodeError:
                continue

            if isinstance(parsed, dict):
                results.append(parsed)

        return results

    @staticmethod
    def _build_response(
        *,
        answer: str,
        tool_results: list[
            dict[str, Any]
        ],
    ) -> SupportAgentResponse:
        for result in reversed(
            tool_results
        ):
            status = result.get("status")

            if status == "proposed":
                proposal = result.get(
                    "proposal",
                    {},
                )

                return SupportAgentResponse(
                    status="proposed",
                    answer=answer,
                    request_reference=(
                        proposal.get(
                            "reference"
                        )
                    ),
                    requires_human=True,
                )

            if status == "created":
                request = result.get(
                    "request",
                    {},
                )

                return SupportAgentResponse(
                    status="created",
                    answer=answer,
                    request_reference=(
                        request.get(
                            "reference"
                        )
                    ),
                    requires_human=True,
                )

            if status in {
                "error",
                "rejected",
            }:
                return SupportAgentResponse(
                    status="error",
                    answer=answer,
                    requires_human=True,
                )

            if (
                status
                == "consent_required"
            ):
                return SupportAgentResponse(
                    status="collecting",
                    answer=answer,
                    requires_human=False,
                )

        return SupportAgentResponse(
            status="collecting",
            answer=answer,
            requires_human=False,
        )