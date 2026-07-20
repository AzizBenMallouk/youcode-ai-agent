from enum import Enum

class KnowledgeGapMatchType(
    str,
    Enum,
):
    EXACT = "exact"
    SEMANTIC = "semantic"
    CREATED = "created"
