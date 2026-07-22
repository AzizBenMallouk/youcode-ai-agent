from datetime import date
from typing import (
    Annotated,
    Literal,
    TypedDict,
)

from langchain_core.messages import (
    BaseMessage,
)
from langgraph.graph.message import (
    add_messages,
)

from youcode_ai.domain.enums import (
    Language,
    RequestType,
)


class SupportDraft(
    TypedDict,
    total=False,
):
    """
    Informations temporairement collectées
    pour une demande de support.

    Ces informations ne sont pas encore
    enregistrées dans la base SQL.
    """

    request_type: RequestType
    language: Language

    email: str
    campus: str

    scheduled_test_date: date
    requested_test_date: date

    description: str

    ambiguities: list[str]


class YouCodeState(
    TypedDict,
    total=False,
):
    """
    State partagé par le graph principal.

    LangGraph conserve cet objet entre les
    différents messages d'une conversation.
    """

    # Historique de la conversation.
    messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    # Identifiant stable de la conversation.
    session_id: str

    # Route choisie par le Supervisor.
    route: Literal[
        "guide",
        "support",
        "newsletter",
        "clarification",
        "out_of_scope",
    ]

    # Agent qui possède actuellement
    # la conversation.
    active_agent: Literal[
        "guide",
        "support",
        "newsletter",
    ]

    # Étape actuelle de la demande Support.
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

    proposed_session_id: str | None
    proposed_test_date: str | None

    rejected_session_ids: list[str]

    # Brouillon temporaire de la demande.
    support_draft: SupportDraft

    # Devient True uniquement après une
    # confirmation explicite du visiteur.
    consent_confirmed: bool

    # Référence créée après l'enregistrement.
    request_reference: str | None

    # Réponse finale retournée au frontend.
    final_response: dict | None

    # Indique si un responsable humain
    # doit intervenir.
    requires_human: bool