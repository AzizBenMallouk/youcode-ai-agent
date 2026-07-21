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


class KnowledgeGapQuestionTable(Base):
    __tablename__ = (
        "knowledge_gap_questions"
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

    session_id: Mapped[
        str | None
    ] = mapped_column(
        String(200),
        nullable=True,
        index=True,
    )

    original_question: Mapped[
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
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    gap: Mapped[
        "KnowledgeGapTable"
    ] = relationship(
        back_populates="questions",
    )