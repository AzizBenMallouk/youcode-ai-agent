import logging
from uuid import uuid4

from youcode_ai.application.ports.email_gateway import (
    EmailDeliveryResult,
    EmailMessage,
)

logger = logging.getLogger(__name__)


class ConsoleEmailGateway:
    """Provider de développement : journalise sans envoyer."""

    def send(
        self,
        message: EmailMessage,
    ) -> EmailDeliveryResult:
        fake_id = f"console-{uuid4().hex[:12]}"

        logger.info(
            "[EMAIL-CONSOLE] To=%s Subject='%s' MessageId=%s",
            message.recipient,
            message.subject,
            fake_id,
        )

        return EmailDeliveryResult(
            success=True,
            provider_message_id=fake_id,
        )
