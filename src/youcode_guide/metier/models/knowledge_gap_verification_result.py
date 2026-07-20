from dataclasses import dataclass
from youcode_guide.metier.models.knowledge_gap_question_verification import KnowledgeGapQuestionVerification


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
