from dataclasses import dataclass
from datetime import date, datetime



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