from typing import TYPE_CHECKING, Any

from langchain_core.messages import AIMessage, HumanMessage
from youcode_ai.agents.guardrails.service import GuardrailAgentService

if TYPE_CHECKING:
    from youcode_ai.orchestration.state import YouCodeState


class GuardrailNodes:
    def __init__(self, service: GuardrailAgentService) -> None:
        self.service = service

    def verify_message(self, state: "YouCodeState") -> dict[str, Any]:
        """Vérifie si le dernier message est sûr."""
        messages = state.get("messages", [])

        last_human_content = None
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                last_human_content = message.content
                break

        if not last_human_content or not isinstance(last_human_content, str):
            return {"active_agent": "guardrail_refusal"}

        result = self.service.invoke(last_human_content)

        if result.is_safe:
            return {"active_agent": "safe"}
        else:
            return {
                "active_agent": "guardrail_refusal",
                "final_response": {
                    "language": "fr",
                    "category": "practical",
                    "answer": f"Désolé, je ne peux pas traiter votre demande. Raison : {result.reason}",
                    "information_available": False,
                    "requires_human": False,
                },
            }

    def refusal(self, state: "YouCodeState") -> dict[str, Any]:
        """Renvoie la réponse de refus directement dans le state."""
        final_response = state.get("final_response", {})
        answer = final_response.get(
            "answer", "Désolé, je ne peux pas répondre à cette demande."
        )
        return {"messages": [AIMessage(content=answer)], "requires_human": False}


def create_guardrail_nodes() -> GuardrailNodes:
    from youcode_ai.agents.guardrails.service import create_guardrail_agent_service

    return GuardrailNodes(create_guardrail_agent_service())
