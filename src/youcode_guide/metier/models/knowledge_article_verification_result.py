from dataclasses import dataclass
from youcode_guide.metier.models.knowledge_gap_verification_result import KnowledgeGapVerificationResult

@dataclass(frozen=True)
class KnowledgeArticleVerificationResult:
    article_id: int
    gap_results: list[
        KnowledgeGapVerificationResult
    ]