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
    KnowledgeAnswerStatus,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class KnowledgeGapAnswerTable(Base):
    __tablename__ = (
        "knowledge_gap_answers"
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    gap_id: Mapped[str] = mapped_column(
        ForeignKey(
            "knowledge_gaps.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    raw_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    structured_answer: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    source_reference: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[
        KnowledgeAnswerStatus
    ] = mapped_column(
        SqlEnum(
            KnowledgeAnswerStatus,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=(
            KnowledgeAnswerStatus.DRAFT
        ),
        index=True,
    )

    created_by: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
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

    published_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    gap: Mapped[
        "KnowledgeGapTable"
    ] = relationship(
        back_populates="answers",
    )