from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class KnowledgeGapStatus(
    str,
    Enum,
):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


@dataclass
class KnowledgeGap:
    """
    Groupe de questions sémantiquement similaires.
    """

    id: int | None
    canonical_question: str
    normalized_question: str
    language: str
    category: str
    occurrence_count: int
    status: KnowledgeGapStatus
    created_at: datetime
    last_asked_at: datetime
    resolved_at: datetime | None = None
    vector_point_id: str | None = None
    indexed_at: datetime | None = None


@dataclass
class KnowledgeGapQuestion:
    """
    Formulation individuelle associée à un groupe.
    """

    id: int | None
    knowledge_gap_id: int
    original_question: str
    normalized_question: str
    question_hash: str
    language: str
    semantic_score: float | None
    created_at: datetime


@dataclass(frozen=True)
class KnowledgeGapDetails:
    gap: KnowledgeGap
    questions: list[KnowledgeGapQuestion]



@dataclass(frozen=True)
class SemanticKnowledgeGapMatch:
    knowledge_gap_id: int
    vector_point_id: str
    canonical_question: str
    category: str
    status: str
    score: float


class KnowledgeGapMatchType(
    str,
    Enum,
):
    EXACT = "exact"
    SEMANTIC = "semantic"
    CREATED = "created"


@dataclass(frozen=True)
class KnowledgeGapReportResult:
    gap: KnowledgeGap
    match_type: KnowledgeGapMatchType
    semantic_score: float | None = None

    
class KnowledgeArticleStatus(
    str,
    Enum,
):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


@dataclass
class KnowledgeArticle:
    id: int | None
    document_key: str
    title: str
    content: str
    category: str
    status: KnowledgeArticleStatus
    version: int
    source_name: str | None
    content_hash: str
    created_by: str
    reviewed_by: str | None
    valid_from: date | None
    valid_until: date | None
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    indexed_at: datetime | None = None


@dataclass(frozen=True)
class KnowledgeGapQuestionVerification:
    question_id: int | None
    question: str
    article_found: bool
    retrieved_parent_count: int


@dataclass(frozen=True)
class KnowledgeGapVerificationResult:
    gap_id: int
    article_id: int
    resolved: bool
    matched_questions: int
    total_questions: int
    coverage: float
    questions: list[
        KnowledgeGapQuestionVerification
    ]


@dataclass(frozen=True)
class KnowledgeArticleVerificationResult:
    article_id: int
    gap_results: list[
        KnowledgeGapVerificationResult
    ]