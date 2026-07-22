from datetime import (
    date,
    datetime,
)
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


RegistrationStatus = Literal[
    "open",
    "upcoming",
    "closed",
    "unknown",
]


class RegistrationPeriod(
    BaseModel
):
    id: str

    program: Literal[
        "full_program",
        "bootcamp",
    ]

    campus: Literal[
        "Safi",
        "Youssoufia",
        "Nador",
        "all",
    ]

    status: RegistrationStatus

    opening_date: date | None = None
    closing_date: date | None = None

    registration_url: str | None = None

    available_places: int | None = Field(
        default=None,
        ge=0,
    )

    message: str | None = Field(
        default=None,
        max_length=500,
    )

    updated_at: datetime


class RegistrationPeriodList(
    BaseModel
):
    items: list[RegistrationPeriod]

    total: int


class RegistrationStatusResponse(
    BaseModel
):
    program: str
    campus: str | None

    status: RegistrationStatus

    opening_date: date | None = None
    closing_date: date | None = None

    registration_url: str | None = None

    available_places: int | None = None

    message: str | None = None

    updated_at: datetime | None = None