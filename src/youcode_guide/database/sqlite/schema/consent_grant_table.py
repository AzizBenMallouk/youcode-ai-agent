from datetime import datetime

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
