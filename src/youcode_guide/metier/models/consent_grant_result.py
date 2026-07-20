from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)
from youcode_guide.metier.enums.consent_purpose import ConsentPurpose


class ConsentGrantResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    reference: str

    token: str

    purpose: ConsentPurpose

    expires_at: datetime

