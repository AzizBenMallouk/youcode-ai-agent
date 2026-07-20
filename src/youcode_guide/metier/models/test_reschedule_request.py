from youcode_guide.metier.models.base_visitor_request import BaseVisitorRequest
from datetime import date
from pydantic import (
    Field,
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
