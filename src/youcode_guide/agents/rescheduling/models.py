from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ReschedulingAgentResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    status: Literal[
        "prepared",
        "proposed",
        "no_session",
        "requires_human",
        "error",
    ]

    answer: str
    reference: str | None = None

    external_session_id: str | None = None
    proposed_test_date: str | None = None

    requires_human: bool