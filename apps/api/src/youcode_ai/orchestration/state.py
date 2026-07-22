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


class SupportDraft(
    TypedDict,
    total=False,
):
    """
    Informations temporairement collectées
    pour une demande de support.

    Toutes les valeurs conservées dans le state
    doivent être sérialisables.
    """

    # Valeurs des enums sous forme de str.
    request_type: str
    language: Literal[
        "fr",
        "en",
        "ar",
        "darija",
    ]

    email: str
    campus: str

    # Dates au format ISO : YYYY-MM-DD.
    scheduled_test_date: str
    requested_test_date: str

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

    # Historique complet de la conversation.
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

    # Réponse finale retournée au frontend.
    final_response: dict | None

    # Indique si un responsable humain
    # doit intervenir.
    requires_human: bool


    # -------------------------------
    # newsletter workflow
    # -------------------------------

    newsletter_phase: Literal[
        "collecting",
        "awaiting_consent",
        "processing",
        "completed",
        "cancelled",
    ]

    # -------------------------------
    # Support workflow
    # -------------------------------

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

    # Date et heure au format ISO.
    proposed_test_date: str | None

    rejected_session_ids: list[str]

    # Brouillon non enregistré en base.
    support_draft: SupportDraft

    # True après confirmation explicite.
    consent_confirmed: bool

    # Référence après enregistrement SQL.
    request_reference: str | None