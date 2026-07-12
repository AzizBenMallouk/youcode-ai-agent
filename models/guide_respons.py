from typing import Literal

from pydantic import BaseModel, Field


class GuideResponse(BaseModel):
    language: Literal["fr", "en", "ar", "darija"] = Field(
        description="Langue principale utilisée par le visiteur."
    )

    category: Literal[
        "general",
        "admission",
        "program",
        "campus",
        "pedagogy",
        "career",
        "event",
        "practical",
        "out_of_scope",
    ] = Field(
        description="Catégorie principale de la demande."
    )

    answer: str = Field(
        min_length=1,
        max_length=1000,
        description="Réponse finale dans la langue du visiteur.",
    )

    information_available: bool = Field(
        description=(
            "Vrai si le contexte officiel contient suffisamment "
            "d'informations pour répondre."
        )
    )

    requires_human: bool = Field(
        description=(
            "Vrai si la demande personnelle nécessite "
            "l'intervention d'un responsable."
        )
    )