from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


SupervisorRoute = Literal[
    "guide",
    "support",
    "newsletter",
    "clarification",
    "out_of_scope",
]


class SupervisorDecision(BaseModel):
    """
    Décision structurée produite par le
    Supervisor.

    Cette décision est interne et ne doit pas
    être montrée au visiteur.
    """

    route: SupervisorRoute

    language: Literal[
        "fr",
        "en",
        "ar",
        "darija",
    ] = "fr"

    clarification_question: str | None = Field(
        default=None,
        max_length=300,
    )

    @field_validator(
        "clarification_question",
        mode="before",
    )
    @classmethod
    def clean_clarification(
        cls,
        value: object,
    ) -> str | None:
        if value is None:
            return None

        text = " ".join(
            str(value).split()
        )

        return text or None

    @field_validator(
        "clarification_question",
        mode="after",
    )
    @classmethod
    def validate_clarification(
        cls,
        value: str | None,
        info,
    ) -> str | None:
        route = info.data.get("route")

        if (
            route == "clarification"
            and not value
        ):
            return (
                "Pouvez-vous préciser votre "
                "demande concernant YouCode ?"
            )

        return value