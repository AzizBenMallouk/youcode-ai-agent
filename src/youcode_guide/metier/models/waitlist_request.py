from youcode_guide.metier.models.base_visitor_request import BaseVisitorRequest
from pydantic import (
    Field,
)

class WaitlistRequest(
    BaseVisitorRequest
):
    campus: str | None = Field(
        default=None,
        max_length=100,
    )


