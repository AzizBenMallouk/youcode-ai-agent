from dataclasses import dataclass
from datetime import date, datetime
from youcode_guide.metier.enums.knowledge_gap_status import KnowledgeGapStatus


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
