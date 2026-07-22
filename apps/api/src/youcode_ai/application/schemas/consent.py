from datetime import datetime

from pydantic import BaseModel

from youcode_ai.domain.enums import (
    ConsentPurpose,
)


class ConsentGrantResult(BaseModel):
    id: str
    reference: str
    purpose: ConsentPurpose
    created_at: datetime
    used_at: datetime