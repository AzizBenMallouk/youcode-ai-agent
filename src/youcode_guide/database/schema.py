from datetime import datetime

from sqlalchemy import (
    DateTime,
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