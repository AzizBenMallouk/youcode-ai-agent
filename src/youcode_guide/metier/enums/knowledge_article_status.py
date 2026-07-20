from enum import Enum

class KnowledgeArticleStatus(
    str,
    Enum,
):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"