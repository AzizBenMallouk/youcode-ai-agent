from datetime import datetime, date

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from youcode_guide.database.sqlite.connection import (
    Base,
)

class VisitorRequestTable(Base):
    __tablename__ = "visitor_requests"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )

    reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    request_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    language: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    campus: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    platform: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    scheduled_test_date: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
    )

    requested_test_date: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
    )

    # ID de la session retournée par l'API externe.
    external_session_id: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # Date et heure proposées par l'agent.
    proposed_test_date: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Explication de l'acceptation ou du refus.
    decision_reason: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    consent_id: Mapped[str] = mapped_column(
        ForeignKey("consent_grants.id"),
        unique=True,
        nullable=False,
    )

    processed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

