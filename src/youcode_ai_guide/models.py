from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Language(Enum):
    FR = "fr"
    EN = "en"
    AR = "ar"
    DARIJA = "darija"


class Category(Enum):
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
    model_config = ConfigDict(extra="forbid")

    language: Language
    category: Category

    answer: str = Field(min_length=1)

    information_available: bool
    requires_human: bool