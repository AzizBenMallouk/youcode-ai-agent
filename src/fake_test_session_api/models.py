from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TestSession(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    id: str
    campus: str

    test_type: Literal[
        "online",
        "presentiel",
    ]

    scheduled_at: datetime

    capacity: int = Field(
        gt=0,
    )

    reserved_places: int = Field(
        ge=0,
    )

    status: Literal[
        "open",
        "full",
        "closed",
        "cancelled",
    ]

    @property
    def available_places(self) -> int:
        return max(
            self.capacity
            - self.reserved_places,
            0,
        )


class TestSessionResponse(BaseModel):
    id: str
    campus: str
    test_type: str
    scheduled_at: datetime
    available_places: int
    status: str


class TestSessionListResponse(BaseModel):
    items: list[TestSessionResponse]
    total: int