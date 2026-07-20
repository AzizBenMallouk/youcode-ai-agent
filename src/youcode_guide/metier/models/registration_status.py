from datetime import datetime
from youcode_guide.metier.enums.registration_state import RegistrationState
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)



class RegistrationStatus(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    status: RegistrationState

    registration_url: HttpUrl | None = None
    opening_date: datetime | None = None
    closing_date: datetime | None = None

    message: str | None = Field(
        default=None,
        max_length=1000,
    )

    updated_at: datetime

