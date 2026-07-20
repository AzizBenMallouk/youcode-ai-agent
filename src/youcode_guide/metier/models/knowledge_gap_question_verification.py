from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeGapQuestionVerification:
    question_id: int | None
    question: str
    article_found: bool
    retrieved_parent_count: int