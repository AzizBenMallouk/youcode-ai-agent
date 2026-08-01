from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SupportDraft(TypedDict, total=False):
    request_type: str
    language: Literal["fr", "en", "ar", "darija"]
    email: str
    phone_number: str
    full_name: str
    cin: str
    campus: str
    scheduled_test_date: str
    requested_test_date: str
    description: str
    ambiguities: list[str]

class SupportState(TypedDict, total=False):
    """State pour l'agent Support."""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    user_id: str
    
    support_phase: Literal[
        "collecting",
        "awaiting_consent",
        "processing",
        "awaiting_session_confirmation",
        "confirming_session",
        "searching_alternative",
        "completed",
        "cancelled",
    ]
    support_draft: SupportDraft
    consent_confirmed: bool
    proposed_session_id: str | None
    proposed_test_date: str | None
    rejected_session_ids: list[str]
    request_reference: str | None
