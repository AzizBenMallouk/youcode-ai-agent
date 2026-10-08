import json
import logging
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from shared.core.llm import create_chat_model
from shared.memory.summarizer import summarize_if_needed

logger = logging.getLogger(__name__)


class AdminNodes:
    """Nœuds du graphe pour l'Agent Admin."""

    def __init__(self):
        self.llm = create_chat_model(use_cache=False)

    async def check_guardrails(self, state: dict) -> dict[str, Any]:
        """Vérifie l'autorisation basée sur le rôle."""
        role = state.get("role", "formateur")
        messages = state.get("messages", [])

        # Apply summarization to keep context manageable
        messages = await summarize_if_needed(messages)

        last_msg = ""
        if messages:
            last_msg = messages[-1].content.lower()

        if role == "formateur" and (
            "finance" in last_msg
            or "budget" in last_msg
            or "salaire" in last_msg
        ):
            return {
                "admin_phase": "rejected",
                "final_response": {
                    "answer": "Accès refusé. En tant que formateur, vous n'êtes pas autorisé à accéder aux données financières."
                },
            }

        return {"admin_phase": "processing"}
