from typing import (
    Any,
    Literal,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class ChatRequest(BaseModel):
    """
    Message envoyé par l'application visiteur.

    Lors du premier message, session_id peut être
    absent. L'API en générera un.
    """

    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    @field_validator(
        "session_id",
        mode="before",
    )
    @classmethod
    def clean_session_id(
        cls,
        value: object,
    ) -> str | None:
        if value is None:
            return None

        session_id = str(value).strip()

        return session_id or None

    @field_validator(
        "message",
        mode="before",
    )
    @classmethod
    def clean_message(
        cls,
        value: object,
    ) -> str:
        return " ".join(
            str(value).split()
        )


class ChatResponse(BaseModel):
    """
    Réponse commune retournée par tous les
    agents.
    """

    session_id: str

    agent: Literal[
        "guide",
        "support",
        "newsletter",
        "supervisor",
    ]

    status: str

    language: Literal[
        "fr",
        "en",
        "ar",
        "darija",
    ] = "fr"

    answer: str

    requires_human: bool = False

    # Informations propres à chaque workflow :
    # référence Support, date proposée,
    # référence Newsletter, catégorie RAG, etc.
    data: dict[str, Any] = Field(
        default_factory=dict
    )


class ChatErrorResponse(BaseModel):
    detail: str