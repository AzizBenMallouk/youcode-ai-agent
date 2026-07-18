from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class Language(str, Enum):
    FR = "fr"
    EN = "en"
    AR = "ar"
    DARIJA = "darija"


class Category(str, Enum):
    GENERAL = "general"
    ADMISSION = "admission"
    PROGRAM = "program"
    CAMPUS = "campus"
    PEDAGOGY = "pedagogy"
    CAREER = "career"
    EVENT = "event"
    PRACTICAL = "practical"
    OUT_OF_SCOPE = "out_of_scope"


class GuideResponse(BaseModel):
    # model_config = ConfigDict(
    #     extra="forbid",
    #     str_strip_whitespace=True,
    # )

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


class SourceReference(BaseModel):
    # model_config = ConfigDict(extra="forbid")

    source: str
    category: str | None = None
    campus: str | None = None
    relevance_score: float | None = None


class KnowledgeResult(BaseModel):
    # model_config = ConfigDict(extra="forbid")

    response: GuideResponse

    sources: list[SourceReference] = Field(
        default_factory=list,
    )

class ContextualizedQuestion(BaseModel):
    # model_config = ConfigDict(
    #     extra="forbid",
    #     str_strip_whitespace=True,
    # )

    search_question: str = Field(
        min_length=1,
        max_length=1000,
        description=(
            "Question autonome en français utilisée "
            "uniquement pour la recherche documentaire"
        ),
    )


class KnowledgeSearchStatus(
    str,
    Enum,
):
    FOUND = "found"
    NOT_FOUND = "not_found"
    TECHNICAL_ERROR = "technical_error"


class KnowledgeSearchResult(BaseModel):
    status: KnowledgeSearchStatus
    query: str
    document_count: int = 0
    context: str = ""
    message: str | None = None