import logging

from youcode_ai.agents.guardrails.agent import create_guardrail_agent
from youcode_ai.agents.guardrails.schemas import GuardrailResult

logger = logging.getLogger(__name__)


class GuardrailAgentService:
    def __init__(self) -> None:
        self.agent = create_guardrail_agent()

    def invoke(self, message: str) -> GuardrailResult:
        try:
            result = self.agent.invoke({"message": message})
            if isinstance(result, GuardrailResult):
                return result
            # Par défaut on bloque en cas de doute
            return GuardrailResult(is_safe=False, reason="Format de réponse invalide.")
        except Exception:
            logger.exception("Erreur lors du guardrail, blocage par précaution.")
            return GuardrailResult(
                is_safe=False, reason="Erreur technique du filtre de sécurité."
            )


def create_guardrail_agent_service() -> GuardrailAgentService:
    return GuardrailAgentService()
