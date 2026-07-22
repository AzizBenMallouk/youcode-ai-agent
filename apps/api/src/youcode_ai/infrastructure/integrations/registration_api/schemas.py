from datetime import (
    date,
    datetime,
)
from typing import Literal

from pydantic import BaseModel


class RegistrationStatusData(
    BaseModel
):
    program: str
    campus: str | None = None

    status: Literal[
        "open",
        "upcoming",
        "closed",
        "unknown",
    ]

    opening_date: date | None = None
    closing_date: date | None = None

    registration_url: str | None = None

    available_places: int | None = None

    message: str | None = None

    updated_at: datetime | None = None