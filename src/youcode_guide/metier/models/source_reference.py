from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class SourceReference(BaseModel):
    source: str
    category: str | None = None
    campus: str | None = None
    relevance_score: float | None = None
