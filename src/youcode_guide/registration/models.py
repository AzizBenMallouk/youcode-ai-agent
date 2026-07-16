from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)


class RegistrationState(str, Enum):
    UNKNOWN = "unknown"
    SCHEDULED = "scheduled"
    OPEN = "open"
    CLOSED = "closed"


class RegistrationStatus(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    status: RegistrationState

    registration_url: HttpUrl | None = None
    opening_date: datetime | None = None
    closing_date: datetime | None = None

    message: str | None = Field(
        default=None,
        max_length=1000,
    )

    updated_at: datetime


class UpdateRegistrationStatus(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    status: RegistrationState

    registration_url: HttpUrl | None = None
    opening_date: datetime | None = None
    closing_date: datetime | None = None

    message: str | None = Field(
        default=None,
        max_length=1000,
    )