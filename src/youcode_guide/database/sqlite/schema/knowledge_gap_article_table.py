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


class KnowledgeGapArticleTable(Base):
    """
    Association entre un knowledge gap et
    l'article qui peut le résoudre.
    """

    __tablename__ = "knowledge_gap_articles"

    knowledge_gap_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "knowledge_gaps.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        )
    )

    knowledge_article_id: Mapped[int] = (
        mapped_column(
            ForeignKey(
                "knowledge_articles.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        )
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

