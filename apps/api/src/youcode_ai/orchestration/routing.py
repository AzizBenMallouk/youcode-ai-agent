from typing import Literal

from youcode_ai.orchestration.state import (
    YouCodeState,
)


# -------------------------------------
# Types de routage globaux
# -------------------------------------

EntryRoute = Literal[
    "supervisor",
    "support_extract",
    "support_consent",
    "support_process",
    "support_session_decision",
    "support_confirm_session",
    "support_alternative",
    "newsletter_extract",
    "newsletter_consent",
    "newsletter_process",
]


SupervisorRoute = Literal[
    "guide",
    "support_extract",
    "newsletter_extract",
    "clarification",
    "out_of_scope",
]


# -------------------------------------
# Types de routage Support
# -------------------------------------

ExtractionRoute = Literal[
    "missing",
    "consent",
    "process",
    "end",
]


ConsentRoute = Literal[
    "support_process",
    "end",
]


SupportEntryRoute = Literal[
    "support_extract",
    "support_consent",
    "support_process",
    "support_session_decision",
    "support_confirm_session",
    "support_alternative",
    "end",
]


SessionDecisionRoute = Literal[
    "support_confirm_session",
    "support_alternative",
    "end",
]


# -------------------------------------
# Types de routage Newsletter
# -------------------------------------

NewsletterEntryRoute = Literal[
    "newsletter_extract",
    "newsletter_consent",
    "newsletter_process",
    "end",
]


NewsletterExtractionRoute = Literal[
    "newsletter_process",
    "end",
]


NewsletterConsentRoute = Literal[
    "newsletter_process",
    "end",
]


# -------------------------------------
# Entrée globale
# -------------------------------------

def route_graph_entry(
    state: YouCodeState,
) -> EntryRoute:
    """
    Décide où envoyer chaque nouveau message.

    Si un workflow possède déjà la conversation,
    le message lui est envoyé directement sans
    repasser par le Supervisor.
    """

    active_agent = state.get(
        "active_agent"
    )

    if active_agent == "support":
        support_route = (
            _get_support_phase_route(
                state
            )
        )

        if support_route != "end":
            return support_route

    if active_agent == "newsletter":
        newsletter_route = (
            _get_newsletter_phase_route(
                state
            )
        )

        if newsletter_route != "end":
            return newsletter_route

    # Aucun workflow actif ou workflow terminé.
    return "supervisor"


# -------------------------------------
# Supervisor
# -------------------------------------

def route_after_supervisor(
    state: YouCodeState,
) -> SupervisorRoute:
    """
    Transforme la décision métier du Supervisor
    en nom de node LangGraph.
    """

    route = state.get("route")

    if route == "guide":
        return "guide"

    if route == "support":
        return "support_extract"

    if route == "newsletter":
        return "newsletter_extract"

    if route == "out_of_scope":
        return "out_of_scope"

    return "clarification"


# -------------------------------------
# Support
# -------------------------------------

def route_after_extraction(
    state: YouCodeState,
) -> ExtractionRoute:
    """
    Choisit la prochaine étape après l'extraction
    des informations Support.
    """

    support_phase = state.get(
        "support_phase"
    )

    if support_phase == "collecting":
        return "missing"

    if (
        support_phase
        == "awaiting_consent"
    ):
        return "consent"

    if (
        support_phase == "processing"
        and state.get(
            "consent_confirmed",
            False,
        )
    ):
        return "process"

    return "end"


def route_support_entry(
    state: YouCodeState,
) -> SupportEntryRoute:
    """
    Sélectionne le node Support correspondant à
    la phase actuelle.
    """

    return _get_support_phase_route(
        state
    )


def _get_support_phase_route(
    state: YouCodeState,
) -> SupportEntryRoute:
    """
    Mapping entre support_phase et les nodes du
    workflow Support.
    """

    support_phase = state.get(
        "support_phase"
    )

    if support_phase == "collecting":
        return "support_extract"

    if (
        support_phase
        == "awaiting_consent"
    ):
        return "support_consent"

    if support_phase == "processing":
        return "support_process"

    if (
        support_phase
        == "awaiting_session_confirmation"
    ):
        return "support_session_decision"

    if (
        support_phase
        == "confirming_session"
    ):
        return "support_confirm_session"

    if (
        support_phase
        == "searching_alternative"
    ):
        return "support_alternative"

    return "end"


def route_after_consent(
    state: YouCodeState,
) -> ConsentRoute:
    """
    Continue vers le traitement uniquement après
    un consentement Support explicite.
    """

    support_phase = state.get(
        "support_phase"
    )

    consent_confirmed = state.get(
        "consent_confirmed",
        False,
    )

    if (
        support_phase == "processing"
        and consent_confirmed
    ):
        return "support_process"

    return "end"


def route_after_session_decision(
    state: YouCodeState,
) -> SessionDecisionRoute:
    """
    Route la décision concernant une proposition
    de session.
    """

    support_phase = state.get(
        "support_phase"
    )

    if (
        support_phase
        == "confirming_session"
    ):
        return "support_confirm_session"

    if (
        support_phase
        == "searching_alternative"
    ):
        return "support_alternative"

    return "end"


# -------------------------------------
# Newsletter
# -------------------------------------

def route_newsletter_entry(
    state: YouCodeState,
) -> NewsletterEntryRoute:
    """
    Sélectionne le node Newsletter correspondant
    à la phase actuelle.
    """

    return _get_newsletter_phase_route(
        state
    )


def _get_newsletter_phase_route(
    state: YouCodeState,
) -> NewsletterEntryRoute:
    """
    Mapping entre newsletter_phase et les nodes
    du workflow Newsletter.
    """

    newsletter_phase = state.get(
        "newsletter_phase"
    )

    if newsletter_phase == "collecting":
        return "newsletter_extract"

    if (
        newsletter_phase
        == "awaiting_consent"
    ):
        return "newsletter_consent"

    if newsletter_phase == "processing":
        return "newsletter_process"

    # completed, cancelled, phase absente ou
    # incorrecte.
    return "end"


def route_after_newsletter_extraction(
    state: YouCodeState,
) -> NewsletterExtractionRoute:
    """
    Après l'extraction :

    - une désinscription complète passe
      directement au traitement ;
    - une inscription attend le consentement ;
    - un brouillon incomplet attend la prochaine
      réponse du visiteur.
    """

    if (
        state.get("newsletter_phase")
        == "processing"
    ):
        return "newsletter_process"

    return "end"


def route_after_newsletter_consent(
    state: YouCodeState,
) -> NewsletterConsentRoute:
    """
    Après le consentement Newsletter :

    - accepté : enregistrement SQL ;
    - refusé ou ambigu : fin du tour.
    """

    newsletter_phase = state.get(
        "newsletter_phase"
    )

    consent_confirmed = state.get(
        "newsletter_consent_confirmed",
        False,
    )

    if (
        newsletter_phase == "processing"
        and consent_confirmed
    ):
        return "newsletter_process"

    return "end"