from datetime import (
    date,
    datetime,
)
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class SupportRequestResponse(
    BaseModel
):
    reference: str

    request_type: str

    status: str

    email: str

    language: Literal[
        "fr",
        "en",
        "ar",
        "darija",
    ]

    campus: str | None = None
    platform: str | None = None
    description: str | None = None

    scheduled_test_date: date | None = None
    requested_test_date: date | None = None

    external_session_id: str | None = None
    proposed_test_date: datetime | None = None

    proposal_justification: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

    review_note: str | None = None
    reviewed_at: datetime | None = None


class SupportRequestListResponse(
    BaseModel
):
    items: list[
        SupportRequestResponse
    ]

    total: int
    page: int
    page_size: int


class ApproveSupportRequest(
    BaseModel
):
    note: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator(
        "note",
        mode="before",
    )
    @classmethod
    def clean_note(
        cls,
        value: object,
    ) -> str | None:
        if value is None:
            return None

        text = " ".join(
            str(value).split()
        )

        return text or None


class RejectSupportRequest(
    BaseModel
):
    reason: str = Field(
        min_length=3,
        max_length=1000,
    )

    @field_validator(
        "reason",
        mode="before",
    )
    @classmethod
    def clean_reason(
        cls,
        value: object,
    ) -> str:
        return " ".join(
            str(value).split()
        )


class SupportRequestActionResponse(
    BaseModel
):
    reference: str

    status: Literal[
        "approved",
        "rejected",
    ]

    message: str