from youcode_guide.metier.models.base_visitor_request import BaseVisitorRequest
from pydantic import (
    Field,
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