from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ExternalTestSession(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    id: str
    campus: str
    test_type: str
    scheduled_at: datetime
    available_places: int | None = None
    status: str


class ExternalTestSessionList(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    items: list[ExternalTestSession]