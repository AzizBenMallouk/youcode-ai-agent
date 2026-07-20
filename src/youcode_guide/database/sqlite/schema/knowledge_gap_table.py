from __future__ import annotations
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
from typing import TYPE_CHECKING
from youcode_guide.database.sqlite.connection import (
    Base,
)


if TYPE_CHECKING:
    from youcode_guide.database.sqlite.schema.knowledge_gap_question_table import (
        KnowledgeGapQuestionTable,
    )




class KnowledgeGapTable(Base):
    """
    Représente un groupe de questions
    sémantiquement similaires.
    """

    __tablename__ = "knowledge_gaps"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    canonical_question: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    normalized_question: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    occurrence_count: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
            default=1,
        )
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    vector_point_id: Mapped[
        str | None
    ] = mapped_column(
        String(36),
        unique=True,
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_asked_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    resolved_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    indexed_at: Mapped[
        datetime | None
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    questions: Mapped[
        list[KnowledgeGapQuestionTable]
    ] = relationship(
        back_populates="knowledge_gap",
        cascade="all, delete-orphan",
    )


