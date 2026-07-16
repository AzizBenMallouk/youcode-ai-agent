from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class ConsentPurpose(str, Enum):
    WAITLIST_NOTIFICATION = (
        "waitlist_notification"
    )

    ACCESS_SUPPORT = "access_support"

    TEST_RESCHEDULE = "test_reschedule"


class CreateConsentGrant(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    session_id: str = Field(
        min_length=5,
        max_length=200,
    )

    purpose: ConsentPurpose

    email: EmailStr

    accepted: bool


class ConsentGrantResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    reference: str

    token: str

    purpose: ConsentPurpose

    expires_at: datetime


class VerifiedConsent(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    consent_id: str
    reference: str
    purpose: ConsentPurpose
    expires_at: datetime