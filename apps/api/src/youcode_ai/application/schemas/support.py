from datetime import (
    date,
    datetime,
)

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_validator,
)

from youcode_ai.domain.enums import (
    Language,
    RequestStatus,
    RequestType,
)


class SupportRequestCreate(BaseModel):
    session_id: str = Field(
        min_length=1,
        max_length=200,
    )

    request_type: RequestType

    email: EmailStr

    language: Language = Language.FR

    campus: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str = Field(
        min_length=5,
        max_length=1000,
    )

    scheduled_test_date: (
        date | None
    ) = None

    requested_test_date: (
        date | None
    ) = None

    @model_validator(mode="after")
    def validate_rescheduling(
        self,
    ) -> "SupportRequestCreate":
        if (
            self.request_type
            != RequestType.TEST_RESCHEDULE
        ):
            return self

        missing_fields: list[str] = []

        if not self.campus:
            missing_fields.append("campus")

        if self.scheduled_test_date is None:
            missing_fields.append(
                "scheduled_test_date"
            )

        if self.requested_test_date is None:
            missing_fields.append(
                "requested_test_date"
            )

        if missing_fields:
            raise ValueError(
                "Missing rescheduling fields: "
                + ", ".join(missing_fields)
            )

        if (
            self.requested_test_date
            <= self.scheduled_test_date
        ):
            raise ValueError(
                "The requested test date must "
                "be after the scheduled test date."
            )

        return self


class SupportRequestResult(BaseModel):
    id: str
    reference: str
    request_type: RequestType
    status: RequestStatus
    email: EmailStr
    language: Language
    campus: str | None
    scheduled_test_date: date | None
    requested_test_date: date | None
    consent_reference: str
    created_at: datetime


class ReschedulingResult(BaseModel):
    reference: str
    status: RequestStatus
    external_session_id: str
    proposed_test_date: datetime
    decision_reason: str
    requires_human: bool