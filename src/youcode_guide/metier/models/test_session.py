from datetime import datetime

from pydantic import BaseModel


class TestSession(BaseModel):
    external_id: str
    campus: str
    test_type: str
    scheduled_at: datetime
    available_places: int | None = None