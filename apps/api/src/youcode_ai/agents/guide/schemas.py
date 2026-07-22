from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from youcode_ai.domain.enums import (
    Language,
)


GuideCategory = Literal[
    "general",
    "admission",
    "program",
    "campus",
    "pedagogy",
    "career",
    "event",
    "practical",
    "out_of_scope",
]


class GuideResponse(BaseModel):
    language: Language = Field(
        description=(
            "Langue dominante du visiteur : "
            "fr, en, ar ou darija."
        ),
    )

    category: GuideCategory = Field(
        description=(
            "Catégorie de la question du "
            "visiteur."
        ),
    )

    answer: str = Field(
        min_length=1,
        max_length=2000,
        description=(
            "Réponse finale courte, claire "
            "et accueillante."
        ),
    )

    information_available: bool = Field(
        description=(
            "True uniquement si les documents "
            "officiels ou une API officielle "
            "contiennent suffisamment "
            "d'informations."
        ),
    )

    requires_human: bool = Field(
        description=(
            "True uniquement lorsqu'une "
            "intervention humaine est réellement "
            "nécessaire."
        ),
    )

    @field_validator(
        "answer",
        mode="before",
    )
    @classmethod
    def clean_answer(
        cls,
        value,
    ) -> str:
        if not isinstance(value, str):
            return value

        cleaned_value = " ".join(
            value.split()
        ).strip()

        if not cleaned_value:
            raise ValueError(
                "Guide answer cannot be empty."
            )

        return cleaned_value[:2000]