from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
)


class TestSessionStatus(str, Enum):
    OPEN = "open"
    FULL = "full"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TestType(str, Enum):
    ONLINE = "online"
    IN_PERSON = "in_person"


class TestSessionData(BaseModel):
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

    available_capacity: int = Field(
        ge=0
    )


class TestSessionListData(BaseModel):
    items: list[TestSessionData]
    total: int = Field(
        ge=0
    )