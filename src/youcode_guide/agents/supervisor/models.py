from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)


class SupervisorDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    route: Literal[
        "guide",
        "rescheduling",
        "clarification",
        "out_of_scope",
    ]

    reason: str

    request_reference: str | None = None