from datetime import datetime, timezone

from sqlalchemy.orm import Session
from youcode_ai.domain.enums import (
    EmailDeliveryStatus,
)
from youcode_ai.infrastructure.database.repositories.base import (
    BaseRepository,
)
from youcode_ai.infrastructure.database.tables.email_delivery import (
    EmailDeliveryTable,
)


class EmailDeliveryRepository(BaseRepository[EmailDeliveryTable]):
    def __init__(
        self,
        *,
        session: Session,
    ) -> None:
        super().__init__(
            session=session,
            model_type=EmailDeliveryTable,
        )

    def get_pending(
        self,
        *,
        batch_size: int = 10,
    ) -> list[EmailDeliveryTable]:
        """Récupère les e-mails en attente d'envoi."""

        from sqlalchemy import select

        now = datetime.now(timezone.utc)

        statement = (
            select(EmailDeliveryTable)
            .where(
                EmailDeliveryTable.status == EmailDeliveryStatus.PENDING,
            )
            .where(
                (EmailDeliveryTable.scheduled_at.is_(None))
                | (EmailDeliveryTable.scheduled_at <= now),
            )
            .order_by(EmailDeliveryTable.created_at)
            .limit(batch_size)
        )

        return list(self.session.scalars(statement).all())

    def get_by_status(
        self,
        *,
        status: EmailDeliveryStatus,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EmailDeliveryTable], int]:
        return self.list_paginated(
            page=page,
            page_size=page_size,
            conditions=[
                EmailDeliveryTable.status == status,
            ],
            order_by=(EmailDeliveryTable.created_at.desc()),
        )

    def get_by_recipient(
        self,
        *,
        email: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EmailDeliveryTable], int]:
        return self.list_paginated(
            page=page,
            page_size=page_size,
            conditions=[
                EmailDeliveryTable.recipient_email == email.strip().lower(),
            ],
            order_by=(EmailDeliveryTable.created_at.desc()),
        )

    def mark_sending(
        self,
        delivery: EmailDeliveryTable,
    ) -> EmailDeliveryTable:
        delivery.status = EmailDeliveryStatus.SENDING
        delivery.attempts = (delivery.attempts or 0) + 1
        self.session.flush()
        return delivery

    def mark_sent(
        self,
        delivery: EmailDeliveryTable,
        *,
        provider_message_id: str | None = None,
    ) -> EmailDeliveryTable:
        delivery.status = EmailDeliveryStatus.SENT
        delivery.sent_at = datetime.now(timezone.utc)
        delivery.provider_message_id = provider_message_id
        delivery.error_message = None
        self.session.flush()
        return delivery

    def mark_failed(
        self,
        delivery: EmailDeliveryTable,
        *,
        error: str,
    ) -> EmailDeliveryTable:
        delivery.status = (
            EmailDeliveryStatus.FAILED
            if ((delivery.attempts or 0) >= 3)
            else EmailDeliveryStatus.PENDING
        )
        delivery.error_message = error
        self.session.flush()
        return delivery

    def list_filtered(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        email_type: str | None = None,
        recipient: str | None = None,
    ) -> tuple[list[EmailDeliveryTable], int]:
        conditions = []

        if status:
            conditions.append(EmailDeliveryTable.status == status)

        if email_type:
            conditions.append(EmailDeliveryTable.email_type == email_type)

        if recipient:
            conditions.append(
                EmailDeliveryTable.recipient_email == recipient.strip().lower()
            )

        return self.list_paginated(
            page=page,
            page_size=page_size,
            conditions=conditions,
            order_by=(EmailDeliveryTable.created_at.desc()),
        )
