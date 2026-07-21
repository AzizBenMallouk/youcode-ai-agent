from enum import Enum


class KnowledgeCategory(str, Enum):
    GENERAL = "general"
    ADMISSION = "admission"
    PROGRAM = "program"
    CAMPUS = "campus"
    PEDAGOGY = "pedagogy"
    CAREER = "career"
    EVENT = "event"
    PRACTICAL = "practical"


class KnowledgeGapStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class KnowledgeAnswerStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"