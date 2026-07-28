from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    user_id: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    response: str
    active_agent: str
    requires_human: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
