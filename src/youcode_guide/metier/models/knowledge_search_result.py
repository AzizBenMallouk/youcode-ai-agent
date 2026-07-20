from youcode_guide.metier.enums.knowledge_search_status import KnowledgeSearchStatus
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class KnowledgeSearchResult(BaseModel):
    status: KnowledgeSearchStatus
    query: str
    document_count: int = 0
    context: str = ""
    message: str | None = None