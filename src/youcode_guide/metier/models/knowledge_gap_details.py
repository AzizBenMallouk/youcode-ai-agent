from dataclasses import dataclass
from youcode_guide.metier.models.knowledge_gap_question import KnowledgeGapQuestion
from youcode_guide.metier.models.knowledge_gap import KnowledgeGap


@dataclass(frozen=True)
class KnowledgeGapDetails:
    gap: KnowledgeGap
    questions: list[KnowledgeGapQuestion]

