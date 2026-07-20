from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)
from youcode_guide.metier.enums.consent_purpose import ConsentPurpose


class CreateConsentGrant(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    session_id: str = Field(
        min_length=5,
        max_length=200,
    )

    purpose: ConsentPurpose

    email: EmailStr

    accepted: bool
