from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from youcode_ai.domain.enums import (
    Language,
    SubscriptionStatus,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class NewsletterSubscriptionTable(Base):
    __tablename__ = (
        "newsletter_subscriptions"
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )

    language: Mapped[
        Language
    ] = mapped_column(
        SqlEnum(
            Language,
            values_callable=enum_values,
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=Language.FR,
    )

    status: Mapped[
        SubscriptionStatus
    ] = mapped_column(
        SqlEnum(
            SubscriptionStatus,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
        index=True,
    )

    consent_id: Mapped[str] = mapped_column(
        ForeignKey(
            "consent_grants.id",
            ondelete="RESTRICT",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    unsubscribed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    consent: Mapped[
        "ConsentGrantTable"
    ] = relationship(
        back_populates=(
            "newsletter_subscription"
        ),
    )

    preferences: Mapped[
        list["NewsletterPreferenceTable"]
    ] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan",
    )

    email_deliveries: Mapped[
        list["EmailDeliveryTable"]
    ] = relationship(
        back_populates="subscription",
    )