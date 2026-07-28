from datetime import (
    date,
    datetime,
)

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
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
    Language,
    RequestStatus,
    RequestType,
)
from shared.infrastructure.database.base import (
    Base,
)
from shared.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class VisitorRequestTable(Base):
    __tablename__ = "visitor_requests"

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

    request_type: Mapped[RequestType] = mapped_column(
        SqlEnum(
            RequestType,
            values_callable=enum_values,
            native_enum=False,
            length=50,
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[RequestStatus] = mapped_column(
        SqlEnum(
            RequestStatus,
            values_callable=enum_values,
            native_enum=False,
            length=50,
        ),
        nullable=False,
        default=RequestStatus.PENDING,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        index=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    full_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    cin: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    language: Mapped[Language] = mapped_column(
        SqlEnum(
            Language,
            values_callable=enum_values,
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=Language.FR,
    )

    campus: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    scheduled_test_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    requested_test_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    external_session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    proposed_test_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    decision_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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

    consent: Mapped["ConsentGrantTable"] = relationship(
        back_populates="visitor_request",
    )

    review_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
