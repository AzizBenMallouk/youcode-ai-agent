from dataclasses import dataclass, field


@dataclass
class AgentRuntimeContext:
    session_id: str

    consent_tokens: dict[
        str,
        str,
    ] = field(
        default_factory=dict
    )

    def get_consent_token(
        self,
        purpose: str,
    ) -> str | None:
        return self.consent_tokens.get(
            purpose
        )