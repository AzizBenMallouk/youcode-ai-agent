from dataclasses import dataclass

@dataclass(frozen=True)
class SemanticKnowledgeGapMatch:
    knowledge_gap_id: int
    vector_point_id: str
    canonical_question: str
    category: str
    status: str
    score: float
