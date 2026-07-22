from typing import Literal

from pydantic import BaseModel


class SupportAgentResponse(BaseModel):
    status: Literal[
        "collecting",
        "created",
        "proposed",
        "cancelled",
        "requires_human",
        "error",
    ]

    answer: str

    request_reference: str | None = None
    requires_human: bool = False