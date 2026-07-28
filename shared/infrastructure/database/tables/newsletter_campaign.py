from datetime import datetime

from sqlalchemy import (
    DateTime,
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
)
from shared.domain.enums.campaign import CampaignStatus
from shared.infrastructure.database.base import Base
from shared.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class NewsletterCampaignTable(Base):
    __tablename__ = "newsletter_campaigns"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    reference: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    template_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="newsletter_content",
    )

    content_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_topics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_campuses: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_languages: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[CampaignStatus] = mapped_column(
        SqlEnum(
            CampaignStatus,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=CampaignStatus.DRAFT,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    total_recipients: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_sent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    total_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
