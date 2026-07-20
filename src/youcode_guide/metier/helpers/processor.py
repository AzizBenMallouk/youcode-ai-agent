from youcode_guide.metier.models.processed_question import ProcessedQuestion

from youcode_guide.metier.helpers.normalizer import (
    create_question_hash,
    normalize_question,
)
from youcode_guide.metier.helpers.sanitizer import (
    sanitize_question,
)



def process_question(
    question: str,
) -> ProcessedQuestion:
    sanitized_question = sanitize_question(
        question,
    )

    if not sanitized_question:
        raise ValueError(
            "Question is empty after sanitization."
        )

    normalized_question = normalize_question(
        sanitized_question,
    )

    if not normalized_question:
        raise ValueError(
            "Question is empty after normalization."
        )

    question_hash = create_question_hash(
        normalized_question,
    )

    return ProcessedQuestion(
        sanitized_question=sanitized_question,
        normalized_question=(
            normalized_question
        ),
        question_hash=question_hash,
    )