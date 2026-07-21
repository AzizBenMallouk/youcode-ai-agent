import re

from youcode_guide.agents.supervisor.factory import (
    create_supervisor_agent,
)
from youcode_guide.agents.supervisor.models import (
    SupervisorDecision,
)


REQUEST_REFERENCE_PATTERN = re.compile(
    r"\bVR-[A-Z0-9-]{4,27}\b",
    flags=re.IGNORECASE,
)


class SupervisorService:
    def __init__(self) -> None:
        self.agent = (
            create_supervisor_agent()
        )

    def route(
        self,
        message: str,
    ) -> SupervisorDecision:
        normalized_message = message.strip()

        if not normalized_message:
            return SupervisorDecision(
                route="clarification",
                reason=(
                    "La demande est vide."
                ),
                request_reference=None,
            )

        result = self.agent.invoke(
            {
                "message": (
                    normalized_message
                ),
            }
        )

        decision = self._validate_result(
            result
        )

        return self._apply_guardrails(
            message=normalized_message,
            decision=decision,
        )

    @staticmethod
    def _validate_result(
        result: object,
    ) -> SupervisorDecision:
        if isinstance(
            result,
            SupervisorDecision,
        ):
            return result

        if isinstance(result, dict):
            return (
                SupervisorDecision
                .model_validate(result)
            )

        raise RuntimeError(
            "Supervisor did not return "
            "a valid routing decision."
        )

    @staticmethod
    def _extract_reference(
        message: str,
    ) -> str | None:
        match = (
            REQUEST_REFERENCE_PATTERN
            .search(message)
        )

        if match is None:
            return None

        return match.group(0).upper()

    def _apply_guardrails(
        self,
        *,
        message: str,
        decision: SupervisorDecision,
    ) -> SupervisorDecision:
        actual_reference = (
            self._extract_reference(
                message
            )
        )

        if (
            decision.route
            == "rescheduling"
            and actual_reference is None
        ):
            return SupervisorDecision(
                route="guide",
                reason=(
                    "Une nouvelle demande de "
                    "report doit d'abord être "
                    "collectée par le Guide Agent."
                ),
                request_reference=None,
            )

        if decision.route == "rescheduling":
            return SupervisorDecision(
                route="rescheduling",
                reason=decision.reason,
                request_reference=(
                    actual_reference
                ),
            )

        return SupervisorDecision(
            route=decision.route,
            reason=decision.reason,
            request_reference=None,
        )