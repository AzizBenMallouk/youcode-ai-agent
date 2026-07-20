from dataclasses import dataclass
from youcode_guide.metier.models.knowledge_gap import KnowledgeGap
from youcode_guide.metier.enums.knowledge_gap_match_type import KnowledgeGapMatchType

@dataclass(frozen=True)
class KnowledgeGapReportResult:
    gap: KnowledgeGap
    match_type: KnowledgeGapMatchType
    semantic_score: float | None = None
