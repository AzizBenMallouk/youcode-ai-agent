from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from shared.domain.enums import (
    EmailDeliveryStatus,
    EmailType,
)
from shared.infrastructure.database.base import (
    Base,
)
from shared.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class EmailDeliveryTable(Base):
    __tablename__ = "email_deliveries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    subscription_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "newsletter_subscriptions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    recipient_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    email_type: Mapped[EmailType] = mapped_column(
        SqlEnum(
            EmailType,
            values_callable=enum_values,
            native_enum=False,
            length=50,
        ),
        nullable=False,
        index=True,
    )

    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[EmailDeliveryStatus] = mapped_column(
        SqlEnum(
            EmailDeliveryStatus,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=(EmailDeliveryStatus.PENDING),
        index=True,
    )

    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    template_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    payload_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    subscription: Mapped["NewsletterSubscriptionTable | None"] = relationship(
        back_populates="email_deliveries",
    )
