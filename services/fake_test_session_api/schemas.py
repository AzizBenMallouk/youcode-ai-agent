from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    computed_field,
)


class TestSessionStatus(str, Enum):
    OPEN = "open"
    FULL = "full"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TestType(str, Enum):
    ONLINE = "online"
    IN_PERSON = "in_person"


class TestSession(BaseModel):
    id: str
    campus: str
    test_type: TestType
    start_at: datetime

    capacity: int = Field(
        ge=0
    )

    registered_candidates: int = Field(
        ge=0
    )

    status: TestSessionStatus

    @computed_field
    @property
    def available_capacity(self) -> int:
        return max(
            self.capacity
            - self.registered_candidates,
            0,
        )


class TestSessionListResponse(
    BaseModel
):
    items: list[TestSession]
    total: int