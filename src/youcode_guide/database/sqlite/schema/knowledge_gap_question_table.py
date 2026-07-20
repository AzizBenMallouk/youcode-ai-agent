from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
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
if TYPE_CHECKING:
    from youcode_guide.database.sqlite.schema.knowledge_gap_table import (
        KnowledgeGapTable,
    )
    

class KnowledgeGapQuestionTable(Base):
    """
    Représente une formulation individuelle
    appartenant à un knowledge gap.
    """

    __tablename__ = "knowledge_gap_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    knowledge_gap_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "knowledge_gaps.id",
                ondelete="CASCADE",
            ),
            nullable=False,
            index=True,
        )
    )

    original_question: Mapped[str] = (
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

    question_hash: Mapped[str] = (
        mapped_column(
            String(64),
            unique=True,
            nullable=False,
            index=True,
        )
    )

    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    semantic_score: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    knowledge_gap: Mapped[
        KnowledgeGapTable
    ] = relationship(
        back_populates="questions",
    )

