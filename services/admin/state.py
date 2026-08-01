from typing import Annotated, Literal, TypedDict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AdminState(TypedDict, total=False):
    """State pour l'agent Admin."""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    role: str
    admin_phase: Literal["processing", "rejected", "completed"]
    final_response: dict[str, Any]
