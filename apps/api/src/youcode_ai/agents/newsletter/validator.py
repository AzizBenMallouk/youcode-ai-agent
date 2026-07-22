from collections.abc import Mapping
from typing import (
    Any,
    Literal,
)

from email_validator import (
    EmailNotValidError,
    validate_email,
)


MissingNewsletterField = Literal[
    "action",
    "email",
    "topics",
]


def normalize_email(
    email: str | None,
) -> str | None:
    """
    Valide et normalise une adresse e-mail.

    check_deliverability=False évite une requête
    DNS pendant la conversation.
    """

    if not email:
        return None

    try:
        result = validate_email(
            email.strip(),
            check_deliverability=False,
        )

        return result.normalized.lower()

    except EmailNotValidError:
        return None


def get_missing_newsletter_fields(
    draft: Mapping[str, Any],
) -> list[MissingNewsletterField]:
    """
    Retourne les informations nécessaires qui
    sont encore absentes ou invalides.
    """

    missing: list[
        MissingNewsletterField
    ] = []

    action = draft.get("action")

    if action not in {
        "subscribe",
        "unsubscribe",
    }:
        missing.append("action")

    email = normalize_email(
        draft.get("email")
    )

    if email is None:
        missing.append("email")

    topics = draft.get(
        "topics",
        [],
    )

    # Les préférences sont obligatoires
    # uniquement pour une inscription.
    if (
        action == "subscribe"
        and not topics
    ):
        missing.append("topics")

    return missing


def newsletter_draft_is_complete(
    draft: Mapping[str, Any],
) -> bool:
    return not get_missing_newsletter_fields(
        draft
    )


QUESTION_BY_FIELD: dict[
    str,
    dict[str, str],
] = {
    "action": {
        "fr": (
            "Souhaitez-vous vous inscrire aux "
            "notifications ou vous désinscrire ?"
        ),
        "en": (
            "Would you like to subscribe to or "
            "unsubscribe from notifications?"
        ),
        "ar": (
            "هل ترغب في الاشتراك في الإشعارات "
            "أم إلغاء الاشتراك؟"
        ),
        "darija": (
            "بغيتي تسجل فالإشعارات ولا تحيد "
            "الاشتراك ديالك؟"
        ),
    },
    "email": {
        "fr": (
            "Quelle adresse e-mail souhaitez-vous "
            "utiliser ?"
        ),
        "en": (
            "Which email address would you like "
            "to use?"
        ),
        "ar": (
            "ما عنوان البريد الإلكتروني الذي "
            "ترغب في استخدامه؟"
        ),
        "darija": (
            "شنو هو الإيميل اللي بغيتي تستعمل؟"
        ),
    },
    "topics": {
        "fr": (
            "Quelles notifications souhaitez-vous "
            "recevoir : inscriptions, bootcamps, "
            "événements ou actualités YouCode ?"
        ),
        "en": (
            "Which notifications would you like: "
            "registrations, bootcamps, events or "
            "YouCode news?"
        ),
        "ar": (
            "ما الإشعارات التي ترغب في تلقيها: "
            "التسجيلات، المعسكرات، الفعاليات أم "
            "أخبار YouCode؟"
        ),
        "darija": (
            "شنو الإشعارات اللي بغيتي توصلك: "
            "التسجيلات، البوتكامبات، الأحداث ولا "
            "أخبار YouCode؟"
        ),
    },
}


def get_newsletter_question(
    *,
    field: MissingNewsletterField,
    language: str,
) -> str:
    translations = QUESTION_BY_FIELD[
        field
    ]

    return translations.get(
        language,
        translations["fr"],
    )