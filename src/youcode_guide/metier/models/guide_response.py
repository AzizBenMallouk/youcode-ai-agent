from youcode_guide.metier.enums.language import Language
from youcode_guide.metier.enums.category import Category

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class GuideResponse(BaseModel):
    language: Language = Field(
        description=(
            "Langue dominante du visiteur : "
            "fr, en, ar ou darija"
        )
    )

    category: Category = Field(
        description="Catégorie principale de la question"
    )

    answer: str = Field(
        min_length=1,
        max_length=2000,
        description=(
            "Réponse finale courte dans la langue "
            "du visiteur"
        ),
    )

    information_available: bool = Field(
        description=(
            "True si les documents officiels permettent "
            "de répondre correctement"
        )
    )

    requires_human: bool = Field(
        description=(
            "True si la demande nécessite "
            "l'intervention d'un responsable"
        )
    )