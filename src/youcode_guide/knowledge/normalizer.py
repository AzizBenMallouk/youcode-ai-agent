import hashlib
import re
import unicodedata


WHITESPACE_PATTERN = re.compile(r"\s+")


ARABIC_DIACRITICS_PATTERN = re.compile(
    r"""
    [\u0610-\u061A
     \u064B-\u065F
     \u0670
     \u06D6-\u06ED]
    """,
    re.VERBOSE,
)


ARABIC_CHARACTER_MAP = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": "",
    }
)


def normalize_question(
    question: str,
) -> str:
    """
    Produit une version stable utilisée pour le hash et
    la recherche de doublons exacts.
    """

    normalized = unicodedata.normalize(
        "NFKC",
        question,
    )

    normalized = normalized.lower().strip()

    normalized = ARABIC_DIACRITICS_PATTERN.sub(
        "",
        normalized,
    )

    normalized = normalized.translate(
        ARABIC_CHARACTER_MAP,
    )

    normalized = _replace_punctuation_with_spaces(
        normalized,
    )

    normalized = WHITESPACE_PATTERN.sub(
        " ",
        normalized,
    )

    return normalized.strip()


def create_question_hash(
    normalized_question: str,
) -> str:
    return hashlib.sha256(
        normalized_question.encode("utf-8"),
    ).hexdigest()


def _replace_punctuation_with_spaces(
    text: str,
) -> str:
    characters: list[str] = []

    for character in text:
        unicode_category = (
            unicodedata.category(character)
        )

        if unicode_category.startswith(
            ("P", "S"),
        ):
            characters.append(" ")
        else:
            characters.append(character)

    return "".join(characters)