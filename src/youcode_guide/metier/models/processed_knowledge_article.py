from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessedKnowledgeArticle:
    title: str
    content: str
    content_hash: str