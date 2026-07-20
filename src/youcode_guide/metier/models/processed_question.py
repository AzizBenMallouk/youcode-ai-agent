from dataclasses import dataclass

@dataclass(frozen=True)
class ProcessedQuestion:
    sanitized_question: str
    normalized_question: str
    question_hash: str