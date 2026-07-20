from enum import Enum

class KnowledgeSearchStatus(
    str,
    Enum,
):
    FOUND = "found"
    NOT_FOUND = "not_found"
    TECHNICAL_ERROR = "technical_error"