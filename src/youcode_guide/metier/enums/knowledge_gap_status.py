from enum import Enum


class KnowledgeGapStatus(
    str,
    Enum,
):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"
