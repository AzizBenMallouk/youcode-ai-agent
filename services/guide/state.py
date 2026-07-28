from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GuideState(TypedDict, total=False):
    """State pour l'agent Guide (RAG Q&A)."""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
