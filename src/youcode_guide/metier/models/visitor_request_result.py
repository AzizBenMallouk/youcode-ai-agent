from youcode_guide.metier.enums.request_type import RequestType
from youcode_guide.metier.enums.request_status import RequestStatus
from datetime import date, datetime
from pydantic import (
    Field,
    ConfigDict,
    BaseModel,
)


class VisitorRequestResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    reference: str

    request_type: RequestType

    status: RequestStatus

    created_at: datetime

    message: str