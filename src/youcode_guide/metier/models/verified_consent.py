from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from youcode_guide.metier.enums.consent_purpose import ConsentPurpose


class VerifiedConsent(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    consent_id: str
    reference: str
    purpose: ConsentPurpose
    expires_at: datetime