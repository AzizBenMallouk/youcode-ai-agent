from typing import Literal

from youcode_ai.orchestration.state import (
    YouCodeState,
)


EntryRoute = Literal[
    "supervisor",
    "support_extract",
    "support_consent",
    "support_process",
]


SupervisorRoute = Literal[
    "guide",
    "support_extract",
    "newsletter",
    "clarification",
    "out_of_scope",
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
]


def route_graph_entry(
    state: YouCodeState,
) -> EntryRoute:
    """
    Décide où envoyer chaque nouveau message.

    Si une conversation Support est déjà en cours,
    le message revient directement au Support sans
    repasser par le Supervisor.
    """

    active_agent = state.get(
        "active_agent"
    )

    support_phase = state.get(
        "support_phase"
    )

    if active_agent != "support":
        return "supervisor"

    if (
        support_phase
        == "awaiting_consent"
    ):
        return "support_consent"

    if support_phase == "processing":
        return "support_process"

    if support_phase == "collecting":
        return "support_extract"

    # Si le workflow Support est terminé ou
    # annulé, une nouvelle conversation repasse
    # par le Supervisor.
    return "supervisor"


def route_after_supervisor(
    state: YouCodeState,
) -> SupervisorRoute:
    """
    Transforme la décision du Supervisor en nom
    de nœud LangGraph.
    """

    route = state.get("route")

    if route == "guide":
        return "guide"

    if route == "support":
        return "support_extract"

    if route == "newsletter":
        return "newsletter"

    if route == "out_of_scope":
        return "out_of_scope"

    return "clarification"


def route_after_consent(
    state: YouCodeState,
) -> ConsentRoute:
    """
    Après la classification du consentement :

    accepted → traitement ;
    refused ou unclear → fin du tour.
    """

    if (
        state.get("support_phase")
        == "processing"
        and state.get(
            "consent_confirmed",
            False,
        )
    ):
        return "support_process"

    return "end"



def route_support_entry(
    state: YouCodeState,
) -> SupportEntryRoute:
    """
    Choisit le premier nœud Support à exécuter
    pour le nouveau message du visiteur.

    Le choix dépend de la phase enregistrée dans
    le checkpoint LangGraph.
    """

    support_phase = state.get(
        "support_phase"
    )

    # Le système a déjà demandé l'autorisation
    # d'enregistrer les données.
    if (
        support_phase
        == "awaiting_consent"
    ):
        return "support_consent"

    # Le consentement vient d'être accepté.
    if support_phase == "processing":
        return "support_process"

    # Une date a été proposée au visiteur.
    if (
        support_phase
        == "awaiting_session_confirmation"
    ):
        return (
            "support_session_decision"
        )

    # Le visiteur a accepté la date.
    if (
        support_phase
        == "confirming_session"
    ):
        return (
            "support_confirm_session"
        )

    # Le visiteur a refusé la date et demande
    # implicitement une autre proposition.
    if (
        support_phase
        == "searching_alternative"
    ):
        return "support_alternative"

    # Premier message ou collecte encore
    # en cours.
    return "support_extract"

def route_after_session_decision(
    state: YouCodeState,
) -> str:
    phase = state.get(
        "support_phase"
    )

    if phase == "confirming_session":
        return "support_confirm_session"

    if phase == "searching_alternative":
        return "support_alternative"

    return "end"