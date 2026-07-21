from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from youcode_ai.domain.enums import (
    NewsletterTopic,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class NewsletterPreferenceTable(Base):
    __tablename__ = (
        "newsletter_preferences"
    )

    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "topic",
            name=(
                "uq_newsletter_subscription_topic"
            ),
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    subscription_id: Mapped[
        str
    ] = mapped_column(
        ForeignKey(
            "newsletter_subscriptions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    topic: Mapped[
        NewsletterTopic
    ] = mapped_column(
        SqlEnum(
            NewsletterTopic,
            values_callable=enum_values,
            native_enum=False,
            length=50,
        ),
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

    subscription: Mapped[
        "NewsletterSubscriptionTable"
    ] = relationship(
        back_populates="preferences",
    )