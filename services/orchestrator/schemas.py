from pydantic import BaseModel


class IncomingMessage(BaseModel):
    user_id: str
    message: str

class OutgoingResponse(BaseModel):
    response: str
    active_agent: str
    requires_human: bool