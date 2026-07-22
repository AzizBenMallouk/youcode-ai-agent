from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from youcode_ai.domain.enums import (
    EmailDeliveryStatus,
    EmailType,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.tables.common import (
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

    subscription_id: Mapped[
        str | None
    ] = mapped_column(
        ForeignKey(
            "newsletter_subscriptions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    recipient_email: Mapped[
        str
    ] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    email_type: Mapped[
        EmailType
    ] = mapped_column(
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

    status: Mapped[
        EmailDeliveryStatus
    ] = mapped_column(
        SqlEnum(
            EmailDeliveryStatus,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=(
            EmailDeliveryStatus.PENDING
        ),
        index=True,
    )

    provider_message_id: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    error_message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    sent_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    subscription: Mapped[
        "NewsletterSubscriptionTable | None"
    ] = relationship(
        back_populates="email_deliveries",
    )