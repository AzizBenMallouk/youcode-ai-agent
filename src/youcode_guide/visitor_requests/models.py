from datetime import date, datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)

from youcode_guide.models import Language


class RequestType(str, Enum):
    WAITLIST = "waitlist"

    ACCESS_PROBLEM = "access_problem"

    TEST_RESCHEDULE = "test_reschedule"


class RequestStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class BaseVisitorRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    session_id: str = Field(
        min_length=5,
        max_length=200,
    )

    email: EmailStr

    language: Language

    consent_token: str = Field(
        min_length=20,
        max_length=500,
    )


class WaitlistRequest(
    BaseVisitorRequest
):
    campus: str | None = Field(
        default=None,
        max_length=100,
    )


class AccessSupportRequest(
    BaseVisitorRequest
):
    platform: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str = Field(
        min_length=5,
        max_length=1000,
    )


class TestRescheduleRequest(
    BaseVisitorRequest
):
    scheduled_test_date: date

    requested_test_date: date | None = None

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class VisitorRequestResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    reference: str

    request_type: RequestType

    status: RequestStatus

    created_at: datetime

    message: str