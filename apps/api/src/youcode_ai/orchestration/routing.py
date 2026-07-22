from typing import Literal

from youcode_ai.orchestration.state import (
    YouCodeState,
)


EntryRoute = Literal[
    "supervisor",
    "support_extract",
    "support_consent",
    "support_process",
    "support_session_decision",
    "support_confirm_session",
    "support_alternative",
    "newsletter",
]


SupervisorRoute = Literal[
    "guide",
    "support_extract",
    "newsletter",
    "clarification",
    "out_of_scope",
]


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
        newsletter_phase = state.get(
            "newsletter_phase"
        )

        if newsletter_phase not in {
            None,
            "completed",
            "cancelled",
        }:
            return "newsletter"

    return "supervisor"


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
        # Une nouvelle demande Support commence
        # par l'extraction des informations.
        return "support_extract"

    if route == "newsletter":
        return "newsletter"

    if route == "out_of_scope":
        return "out_of_scope"

    return "clarification"


def route_after_extraction(
    state: YouCodeState,
) -> ExtractionRoute:
    """
    Choisit la prochaine étape après l'extraction
    des informations Support.

    collecting :
        il manque des informations ;

    awaiting_consent :
        le brouillon est complet et le
        consentement doit être demandé ;

    processing :
        le consentement est confirmé et la
        demande peut être enregistrée ;

    autre :
        fin du tour ou workflow terminé.
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
    Sélectionne le node Support correspondant
    à la phase actuelle.
    """

    return _get_support_phase_route(
        state
    )


def _get_support_phase_route(
    state: YouCodeState,
) -> SupportEntryRoute:
    """
    Mapping centralisé entre support_phase et
    les nodes du workflow Support.
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

    # Phases completed, cancelled, absentes
    # ou incorrectes.
    return "end"


def route_after_consent(
    state: YouCodeState,
) -> ConsentRoute:
    """
    Après l'analyse du consentement :

    - accepté : traitement de la demande ;
    - refusé : fin du tour ;
    - ambigu : fin du tour après avoir demandé
      une réponse oui/non.
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
    Après la réponse du candidat concernant la
    session proposée :

    - acceptée : confirmation de la proposition ;
    - refusée : recherche d'une autre session ;
    - ambiguë : fin du tour après avoir demandé
      une réponse oui/non.
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