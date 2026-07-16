from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from youcode_guide.database.connection import (
    Base,
)

class RegistrationSettingsTable(Base):
    __tablename__ = "registration_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="unknown",
    )

    registration_url: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    opening_date: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closing_date: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    message: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )



class ConsentGrantTable(Base):
    __tablename__ = "consent_grants"

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

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    purpose: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    subject_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
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

    consent_id: Mapped[str] = mapped_column(
        ForeignKey("consent_grants.id"),
        unique=True,
        nullable=False,
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