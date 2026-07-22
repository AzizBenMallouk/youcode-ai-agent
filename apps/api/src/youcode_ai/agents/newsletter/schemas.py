from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


NewsletterAction = Literal[
    "subscribe",
    "unsubscribe",
    "unknown",
]


NewsletterTopic = Literal[
    "full_program_registration",
    "bootcamps",
    "events",
    "youcode_news",
]


class NewsletterExtraction(BaseModel):
    """
    Informations extraites du message du
    visiteur par le LLM.

    Aucun enregistrement SQL n'est effectué
    pendant cette extraction.
    """

    action: NewsletterAction = "unknown"

    language: Literal[
        "fr",
        "en",
        "ar",
        "darija",
    ] = "fr"

    email: str | None = Field(
        default=None,
        max_length=320,
    )

    topics: list[
        NewsletterTopic
    ] = Field(
        default_factory=list,
    )

    ambiguities: list[str] = Field(
        default_factory=list,
        max_length=5,
    )

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: object,
    ) -> str | None:
        if value is None:
            return None

        email = str(value).strip().lower()

        return email or None

    @field_validator(
        "topics",
        mode="after",
    )
    @classmethod
    def remove_duplicate_topics(
        cls,
        topics: list[NewsletterTopic],
    ) -> list[NewsletterTopic]:
        return list(
            dict.fromkeys(topics)
        )


class NewsletterConsentDecision(
    BaseModel
):
    """
    Classification d'une réponse à la demande
    de consentement.
    """

    decision: Literal[
        "accepted",
        "refused",
        "unclear",
    ]


class NewsletterResponse(BaseModel):
    """
    Réponse publique retournée au frontend.
    """

    status: Literal[
        "collecting",
        "awaiting_consent",
        "subscribed",
        "unsubscribed",
        "cancelled",
        "error",
    ]

    language: Literal[
        "fr",
        "en",
        "ar",
        "darija",
    ]

    answer: str = Field(
        min_length=1,
        max_length=1000,
    )

    subscription_reference: (
        str | None
    ) = None

    requires_human: bool = False

    @field_validator(
        "answer",
        mode="before",
    )
    @classmethod
    def clean_answer(
        cls,
        value: object,
    ) -> str:
        return " ".join(
            str(value).split()
        )