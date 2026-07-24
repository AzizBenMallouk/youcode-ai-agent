from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class EmailMessage:
    """Message e-mail à envoyer."""

    recipient: str
    subject: str
    body_html: str
    body_text: str = ""
    from_address: str = ""
    from_name: str = ""
    reply_to: str = ""
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EmailDeliveryResult:
    """Résultat d'envoi d'un e-mail."""

    success: bool
    provider_message_id: str | None = None
    error_message: str | None = None


class EmailGateway(Protocol):
    """Port d'envoi d'e-mails."""

    def send(
        self,
        message: EmailMessage,
    ) -> EmailDeliveryResult: ...
