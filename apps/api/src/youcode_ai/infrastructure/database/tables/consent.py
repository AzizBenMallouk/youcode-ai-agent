from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from youcode_ai.domain.enums import (
    ConsentPurpose,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class ConsentGrantTable(Base):
    __tablename__ = "consent_grants"

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

    session_id: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    purpose: Mapped[
        ConsentPurpose
    ] = mapped_column(
        SqlEnum(
            ConsentPurpose,
            values_callable=enum_values,
            native_enum=False,
            length=50,
        ),
        nullable=False,
        index=True,
    )

    subject_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    consent_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    expires_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    visitor_request: Mapped[
        "VisitorRequestTable | None"
    ] = relationship(
        back_populates="consent",
        uselist=False,
    )

    newsletter_subscription: Mapped[
        "NewsletterSubscriptionTable | None"
    ] = relationship(
        back_populates="consent",
        uselist=False,
    )