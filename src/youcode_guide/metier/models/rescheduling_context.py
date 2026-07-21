from pydantic import BaseModel

from youcode_guide.metier.models.test_session import (
    TestSession,
)


class ReschedulingContext(BaseModel):
    request_id: str
    reference: str
    email: str
    campus: str

    description: str | None

    scheduled_test_date: str | None
    requested_test_date: str | None

    available_sessions: list[TestSession]

    requires_human: bool = False
    message: str | None = None