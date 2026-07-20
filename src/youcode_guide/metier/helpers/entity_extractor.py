from dataclasses import dataclass

from youcode_guide.metier.helpers.normalizer import (
    normalize_question,
)


CAMPUS_ALIASES = {
    "youssoufia": {
        "youssoufia",
        "yousoufia",
        "يوسفية",
        "اليوسفية",
    },
    "safi": {
        "safi",
        "asfi",
        "آسفي",
        "اسفي",
    },
    "nador": {
        "nador",
        "الناظور",
        "ناظور",
    },
}


@dataclass(frozen=True)
class QuestionEntities:
    campuses: frozenset[str]


def extract_entities(
    question: str,
) -> QuestionEntities:
    normalized_question = normalize_question(
        question,
    )

    campuses: set[str] = set()

    for canonical_name, aliases in (
        CAMPUS_ALIASES.items()
    ):
        normalized_aliases = {
            normalize_question(alias)
            for alias in aliases
        }

        if any(
            _contains_expression(
                normalized_question,
                alias,
            )
            for alias in normalized_aliases
        ):
            campuses.add(canonical_name)

    return QuestionEntities(
        campuses=frozenset(campuses),
    )


def entities_are_compatible(
    first_question: str,
    second_question: str,
) -> bool:
    first_entities = extract_entities(
        first_question,
    )

    second_entities = extract_entities(
        second_question,
    )

    return (
        first_entities.campuses
        == second_entities.campuses
    )


def _contains_expression(
    text: str,
    expression: str,
) -> bool:
    text_words = set(text.split())
    expression_words = expression.split()

    if len(expression_words) == 1:
        return expression in text_words

    return expression in text