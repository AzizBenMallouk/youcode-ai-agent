from dataclasses import dataclass
from datetime import date, datetime
from youcode_guide.metier.enums.knowledge_article_status import KnowledgeArticleStatus

@dataclass
class KnowledgeArticle:
    id: int | None
    document_key: str
    title: str
    content: str
    category: str
    status: KnowledgeArticleStatus
    version: int
    source_name: str | None
    content_hash: str
    created_by: str
    reviewed_by: str | None
    valid_from: date | None
    valid_until: date | None
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    indexed_at: datetime | None = None
