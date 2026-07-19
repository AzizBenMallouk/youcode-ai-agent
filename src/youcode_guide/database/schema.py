from __future__ import annotations

from datetime import date, datetime

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


class KnowledgeArticleTable(Base):
    """
    Réponse ou information officielle ajoutée
    par un administrateur.
    """

    __tablename__ = "knowledge_articles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_key: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft",
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    source_name: Mapped[
        str | None
    ] = mapped_column(
        String(255),
        nullable=True,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reviewed_by: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    valid_from: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
    )

    valid_until: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
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

    published_at: Mapped[
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

