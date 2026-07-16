from typing import Any
from dataclasses import dataclass
import json

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage
)

from youcode_guide.agent.context import AgentRuntimeContext
from youcode_guide.agent.factory import create_youcode_agent
from youcode_guide.models import GuideResponse



@dataclass
class PendingConsent:
    purpose: str
    email: str


@dataclass
class AgentTurnResult:
    response: GuideResponse
    pending_consent: PendingConsent | None


class YouCodeAgentService:
    def __init__(self) -> None:
        self.agent = create_youcode_agent()

    def ask(
        self,
        *,
        session_id: str,
        question: str,
        consent_tokens: dict[str, str] | None = None,
    ) -> GuideResponse:
        runtime_context = AgentRuntimeContext(
            session_id=session_id,
            consent_tokens=consent_tokens or {},
        )

        result: dict[str, Any] = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=question),
                ],
            },
            config={
                "configurable": {
                    "thread_id": session_id,
                },
            },
            context=runtime_context,
        )

        structured_response = result.get("structured_response")

        if structured_response is None:
            raise RuntimeError(
                "L'agent n'a pas produit de réponse structurée."
            )
        

        response = GuideResponse.model_validate(
            structured_response,
        )

        messages = result.get("messages", [])

        pending_consent = self._find_pending_consent(
            messages,
        )

        return AgentTurnResult(
            response=response,
            pending_consent=pending_consent,
        )
    

    def _find_pending_consent(
        self,
        messages: list[BaseMessage],
    ) -> PendingConsent | None:
        current_turn_messages = self._current_turn_messages(
            messages,
        )

        for message in reversed(current_turn_messages):
            if not isinstance(message, ToolMessage):
                continue

            content = self._parse_tool_content(
                message.content,
            )

            if content.get("status") != "consent_required":
                continue

            purpose = content.get("purpose")
            email = content.get("email")

            if purpose and email:
                return PendingConsent(
                    purpose=purpose,
                    email=email,
                )

        return None

    @staticmethod
    def _current_turn_messages(
        messages: list[BaseMessage],
    ) -> list[BaseMessage]:
        last_human_index = 0

        for index, message in enumerate(messages):
            if isinstance(message, HumanMessage):
                last_human_index = index

        return messages[last_human_index:]

    @classmethod
    def _parse_tool_content(
        cls,
        content: Any,
    ) -> dict[str, Any]:
        if isinstance(content, dict):
            return content

        # Certains modèles retournent une liste de blocs.
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    block_content = (
                        block.get("text")
                        or block.get("content")
                    )

                    if block_content is not None:
                        parsed = cls._parse_tool_content(
                            block_content,
                        )

                        if parsed:
                            return parsed

            return {}

        if not isinstance(content, str):
            return {}

        # Format JSON normal.
        try:
            parsed = json.loads(content)

            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        # Compatibilité temporaire avec les anciens tools
        # qui retournaient la représentation Python d'un dict.
        try:
            parsed = ast.literal_eval(content)

            if isinstance(parsed, dict):
                return parsed
        except (ValueError, SyntaxError):
            pass

        return {}