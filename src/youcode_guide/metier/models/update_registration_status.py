from datetime import datetime
from youcode_guide.metier.enums.registration_state import RegistrationState

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
)




class UpdateRegistrationStatus(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    status: RegistrationState

    registration_url: HttpUrl | None = None
    opening_date: datetime | None = None
    closing_date: datetime | None = None

    message: str | None = Field(
        default=None,
        max_length=1000,
    )