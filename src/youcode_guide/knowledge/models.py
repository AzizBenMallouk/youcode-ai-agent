from dataclasses import dataclass
from datetime import datetime
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