from __future__ import annotations

import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from youcode_ai.application.ports.email_gateway import (
    EmailGateway,
    EmailMessage,
)
from youcode_ai.core.config import settings
from youcode_ai.domain.enums import (
    EmailDeliveryStatus,
    EmailType,
)
from youcode_ai.domain.exceptions import (
    EmailDeliveryError,
)
from youcode_ai.infrastructure.database.repositories.email_delivery import (
    EmailDeliveryRepository,
)
from youcode_ai.infrastructure.database.tables.email_delivery import (
    EmailDeliveryTable,
)
from youcode_ai.infrastructure.email.templates import (
    EmailTemplateRenderer,
)

logger = logging.getLogger(__name__)


class EmailService:
    """Service applicatif d'envoi d'e-mails via outbox."""

    def __init__(
        self,
        *,
        session: Session,
        gateway: EmailGateway,
    ) -> None:
        self._session = session
        self._gateway = gateway
        self._repository = (
            EmailDeliveryRepository(
                session=session
            )
        )
        self._renderer = EmailTemplateRenderer()

    def queue_email(
        self,
        *,
        recipient: str,
        email_type: EmailType,
        template_name: str,
        payload: dict | None = None,
        subscription_id: str | None = None,
        scheduled_at: datetime | None = None,
    ) -> EmailDeliveryTable:
        """Crée une entrée outbox sans envoyer."""

        safe_payload = payload or {}

        subject, _, _ = self._renderer.render(
            template_name,
            safe_payload,
        )

        delivery = EmailDeliveryTable(
            recipient_email=(
                recipient.strip().lower()
            ),
            email_type=email_type,
            subject=subject,
            template_name=template_name,
            payload_json=json.dumps(
                safe_payload,
                ensure_ascii=False,
            ),
            status=EmailDeliveryStatus.PENDING,
            attempts=0,
            subscription_id=subscription_id,
            scheduled_at=scheduled_at,
        )

        return self._repository.add(delivery)

    def process_pending(
        self,
        *,
        batch_size: int = 10,
    ) -> list[str]:
        """Traite les e-mails en attente."""

        sent_ids: list[str] = []
        max_attempts = (
            settings.email_max_attempts
        )

        deliveries = (
            self._repository.get_pending(
                batch_size=batch_size
            )
        )

        for delivery in deliveries:
            if delivery.status == (
                EmailDeliveryStatus.SENT
            ):
                continue

            if (
                delivery.attempts or 0
            ) >= max_attempts:
                delivery.status = (
                    EmailDeliveryStatus.FAILED
                )
                self._session.flush()
                continue

            self._send_delivery(delivery)

            if delivery.status == (
                EmailDeliveryStatus.SENT
            ):
                sent_ids.append(delivery.id)

        return sent_ids

    def _send_delivery(
        self,
        delivery: EmailDeliveryTable,
    ) -> None:
        """Envoie un e-mail individuel."""

        self._repository.mark_sending(
            delivery
        )
        self._session.flush()

        try:
            payload = {}
            if delivery.payload_json:
                payload = json.loads(
                    delivery.payload_json
                )

            subject, body_html, body_text = (
                self._renderer.render(
                    delivery.template_name
                    or "default",
                    payload,
                )
            )

            message = EmailMessage(
                recipient=(
                    delivery.recipient_email
                ),
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                from_address=(
                    settings.email_from_address
                ),
                from_name=(
                    settings.email_from_name
                ),
            )

            result = self._gateway.send(
                message
            )

            if result.success:
                self._repository.mark_sent(
                    delivery,
                    provider_message_id=(
                        result.provider_message_id
                    ),
                )

                logger.info(
                    "Email sent: id=%s "
                    "to=%s type=%s",
                    delivery.id,
                    delivery.recipient_email,
                    delivery.email_type.value,
                )
            else:
                self._repository.mark_failed(
                    delivery,
                    error=(
                        result.error_message
                        or "Unknown error"
                    ),
                )

                logger.warning(
                    "Email failed: id=%s "
                    "to=%s attempt=%d",
                    delivery.id,
                    delivery.recipient_email,
                    delivery.attempts,
                )

        except Exception as exc:
            logger.error(
                "Email error: id=%s "
                "error_type=%s",
                delivery.id,
                type(exc).__name__,
            )

            self._repository.mark_failed(
                delivery,
                error=str(exc),
            )

    def get_delivery(
        self,
        *,
        delivery_id: str,
    ) -> EmailDeliveryTable | None:
        return self._repository.get_by_id(
            delivery_id
        )
