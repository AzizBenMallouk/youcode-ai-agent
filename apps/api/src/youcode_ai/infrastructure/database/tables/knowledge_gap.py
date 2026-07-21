from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from youcode_ai.domain.enums import (
    KnowledgeCategory,
    KnowledgeGapStatus,
    Language,
)
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.tables.common import (
    enum_values,
    generate_uuid,
    utc_now,
)


class KnowledgeGapTable(Base):
    __tablename__ = "knowledge_gaps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    canonical_question: Mapped[
        str
    ] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_question: Mapped[
        str
    ] = mapped_column(
        Text,
        nullable=False,
        index=True,
    )

    category: Mapped[
        KnowledgeCategory
    ] = mapped_column(
        SqlEnum(
            KnowledgeCategory,
            values_callable=enum_values,
            native_enum=False,
            length=50,
        ),
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
        index=True,
    )

    status: Mapped[
        KnowledgeGapStatus
    ] = mapped_column(
        SqlEnum(
            KnowledgeGapStatus,
            values_callable=enum_values,
            native_enum=False,
            length=30,
        ),
        nullable=False,
        default=KnowledgeGapStatus.PENDING,
        index=True,
    )

    occurrence_count: Mapped[
        int
    ] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    vector_point_id: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
    )

    admin_notes: Mapped[
        str | None
    ] = mapped_column(
        Text,
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

    resolved_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    questions: Mapped[
        list["KnowledgeGapQuestionTable"]
    ] = relationship(
        back_populates="gap",
        cascade=(
            "all, delete-orphan"
        ),
    )

    answers: Mapped[
        list["KnowledgeGapAnswerTable"]
    ] = relationship(
        back_populates="gap",
        cascade=(
            "all, delete-orphan"
        ),
    )