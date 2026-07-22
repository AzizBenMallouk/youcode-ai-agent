from functools import lru_cache

from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from youcode_ai.agents.support.nodes import (
    create_support_nodes,
)
from youcode_ai.agents.guide.nodes import (
    create_guide_nodes,
)
from youcode_ai.orchestration.routing import (
    route_after_consent,
    route_support_entry,
    route_after_session_decision
)
from youcode_ai.orchestration.state import (
    YouCodeState,
)

def create_youcode_graph():
    support_nodes = create_support_nodes()
    guide_nodes = create_guide_nodes()

    workflow = StateGraph(
        YouCodeState
    )

    workflow.add_node(
        "support_extract",
        support_nodes.extract_information,
    )

    workflow.add_node(
        "support_missing",
        (
            support_nodes
            .request_missing_information
        ),
    )

    workflow.add_node(
        "support_consent",
        support_nodes.classify_consent,
    )

    workflow.add_node(
        "support_process",
        support_nodes.process_request,
    )

    workflow.add_node(
        "support_session_decision",
        support_nodes.classify_session_proposal,
    )

    workflow.add_node(
        "support_confirm_session",
        support_nodes.confirm_session_proposal,
    )

    workflow.add_node(
        "support_alternative",
        support_nodes.search_alternative_session,
    )

    workflow.add_node(
        "guide",
        guide_nodes.answer_question,
    )

    # Chaque nouveau message entre ici.
    # Le routeur regarde la phase Support
    # conservée dans le state.
    workflow.add_conditional_edges(
        START,
        route_support_entry,
        {
            "support_extract": (
                "support_extract"
            ),
            "support_consent": (
                "support_consent"
            ),
            "support_process": (
                "support_process"
            ),
            "support_session_decision": (
                "support_session_decision"
            ),
            "support_confirm_session": (
                "support_confirm_session"
            ),
            "support_alternative": (
                "support_alternative"
            ),
        },
    )

    # Après l'extraction LLM, Python vérifie
    # les informations manquantes.
    workflow.add_edge(
        "support_extract",
        "support_missing",
    )

    # Une question est produite, puis le tour
    # actuel se termine.
    workflow.add_edge(
        "support_missing",
        END,
    )

    # Après le consentement :
    # - accepted → traitement ;
    # - refused/unclear → fin du tour.
    workflow.add_conditional_edges(
        "support_consent",
        route_after_consent,
        {
            "support_process": (
                "support_process"
            ),
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "support_session_decision",
        route_after_session_decision,
        {
            "support_confirm_session": (
                "support_confirm_session"
            ),
            "support_alternative": (
                "support_alternative"
            ),
            "end": END,
        },
    )

    workflow.add_edge(
        "support_confirm_session",
        END,
    )

    workflow.add_edge(
        "support_alternative",
        END,
    )

    workflow.add_edge(
        "support_process",
        END,
    )

    workflow.add_edge(
        START,
        "guide",
    )

    workflow.add_edge(
        "guide",
        END,
    )

    checkpointer = InMemorySaver()

    return workflow.compile(
        checkpointer=checkpointer
    )


@lru_cache(maxsize=1)
def get_youcode_graph():
    """
    Retourne toujours la même instance.

    C'est indispensable avec InMemorySaver :
    recréer le graph ferait perdre les
    conversations précédentes.
    """

    return create_youcode_graph()