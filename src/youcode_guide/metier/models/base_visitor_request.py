from youcode_guide.metier.enums.language import Language

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class BaseVisitorRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    session_id: str = Field(
        min_length=5,
        max_length=200,
    )

    email: EmailStr

    language: Language

    consent_token: str = Field(
        min_length=20,
        max_length=500,
    )