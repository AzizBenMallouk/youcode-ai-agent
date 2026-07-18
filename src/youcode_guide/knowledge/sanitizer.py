import re


EMAIL_PATTERN = re.compile(
    r"""
    \b
    [A-Za-z0-9._%+-]+
    @
    [A-Za-z0-9.-]+
    \.[A-Za-z]{2,}
    \b
    """,
    re.VERBOSE,
)


URL_PATTERN = re.compile(
    r"""
    https?://[^\s]+
    |
    www\.[^\s]+
    """,
    re.VERBOSE | re.IGNORECASE,
)


PHONE_PATTERN = re.compile(
    r"""
    (?<!\w)
    (?:\+?\d[\s().-]*){8,15}
    (?!\w)
    """,
    re.VERBOSE,
)


SECRET_PATTERN = re.compile(
    r"""
    \b
    (
        password
        |
        mot[\s_-]*de[\s_-]*passe
        |
        passwd
        |
        token
        |
        api[\s_-]*key
        |
        secret
        |
        code[\s_-]*de[\s_-]*verification
    )
    \s*[:=]\s*
    [^\s,;]+
    """,
    re.VERBOSE | re.IGNORECASE,
)


LONG_TOKEN_PATTERN = re.compile(
    r"""
    \b
    [A-Za-z0-9_-]{32,}
    \b
    """,
    re.VERBOSE,
)


MULTIPLE_SPACES_PATTERN = re.compile(
    r"\s+"
)


def sanitize_question(
    question: str,
) -> str:
    """
    Retire les données sensibles les plus courantes avant
    d'enregistrer une question comme knowledge gap.

    Cette fonction ne remplace pas une solution complète de
    détection des données personnelles.
    """

    sanitized = question.strip()

    sanitized = EMAIL_PATTERN.sub(
        " ",
        sanitized,
    )

    sanitized = URL_PATTERN.sub(
        " ",
        sanitized,
    )

    sanitized = PHONE_PATTERN.sub(
        " ",
        sanitized,
    )

    sanitized = SECRET_PATTERN.sub(
        " ",
        sanitized,
    )

    sanitized = LONG_TOKEN_PATTERN.sub(
        " ",
        sanitized,
    )

    sanitized = MULTIPLE_SPACES_PATTERN.sub(
        " ",
        sanitized,
    )

    return sanitized.strip()