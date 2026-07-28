from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class OrchestratorState(TypedDict, total=False):
    """State partagé par le graph principal (Superviseur/Wrapper)."""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    user_id: str
    route: Literal["guide", "support", "newsletter", "clarification", "out_of_scope"]
    active_agent: Literal["guide", "support", "newsletter"]
    final_response: dict | None
    requires_human: bool
