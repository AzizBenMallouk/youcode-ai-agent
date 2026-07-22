from dataclasses import dataclass


@dataclass(frozen=True)
class SupportAgentContext:
    session_id: str
    consent_confirmed: bool = False