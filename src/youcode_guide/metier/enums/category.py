from enum import Enum

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