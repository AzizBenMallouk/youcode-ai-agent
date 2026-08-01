from typing import Annotated, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class NewsletterDraft(TypedDict, total=False):
    action: Literal["subscribe", "unsubscribe", "unknown"]
    language: Literal["fr", "en", "ar", "darija"]
    email: str
    phone_number: str
    full_name: str

    topics: list[Literal["full_program_registration", "bootcamps", "events", "youcode_news"]]
    ambiguities: list[str]

class NewsletterState(TypedDict, total=False):
    """State pour l'agent Newsletter."""
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    user_id: str
    
    newsletter_phase: Literal[
        "collecting",
        "awaiting_consent",
        "processing",
        "completed",
        "cancelled",
    ]
    newsletter_draft: NewsletterDraft
    newsletter_consent_confirmed: bool
    subscription_reference: str | None
