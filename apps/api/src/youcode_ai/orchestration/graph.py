from typing import Any
from functools import lru_cache

from langchain_core.messages import (
    AIMessage,
)
from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from youcode_ai.agents.guide.nodes import (
    create_guide_nodes,
)
from youcode_ai.agents.supervisor.nodes import (
    create_supervisor_nodes,
)
from youcode_ai.agents.support.nodes import (
    SupportNodes,
)
from youcode_ai.orchestration.routing import (
    route_after_consent,
    route_after_session_decision,
    route_after_supervisor,
    route_graph_entry,
    route_after_extraction,
)
from youcode_ai.orchestration.state import (
    YouCodeState,
)


def newsletter_not_implemented(
    state: YouCodeState,
) -> dict[str, Any]:
    """
    Node temporaire jusqu'à l'implémentation du
    Newsletter Agent.
    """

    answer = (
        "L'inscription aux notifications sera "
        "bientôt disponible."
    )

    return {
        "active_agent": "newsletter",
        "newsletter_phase": "completed",
        "requires_human": False,
        "messages": [
            AIMessage(
                content=answer
            )
        ],
        "final_response": {
            "status": "not_available",
            "language": "fr",
            "answer": answer,
            "requires_human": False,
        },
    }


@lru_cache(maxsize=1)
def create_youcode_graph():
    workflow = StateGraph(
        YouCodeState
    )

    supervisor_nodes = (
        create_supervisor_nodes()
    )

    guide_nodes = create_guide_nodes()

    support_nodes = SupportNodes()

    # ---------------------------------
    # Supervisor
    # ---------------------------------

    workflow.add_node(
        "supervisor",
        supervisor_nodes.route_message,
    )

    workflow.add_node(
        "clarification",
        supervisor_nodes.clarification,
    )

    workflow.add_node(
        "out_of_scope",
        supervisor_nodes.out_of_scope,
    )

    # ---------------------------------
    # Guide
    # ---------------------------------

    workflow.add_node(
        "guide",
        guide_nodes.answer_question,
    )

    # ---------------------------------
    # Support
    # ---------------------------------

    workflow.add_node(
        "support_extract",
        support_nodes.extract_request,
    )

    workflow.add_node(
        "support_missing",
        support_nodes.request_missing_information,
    )

    workflow.add_node(
        "support_consent",
        support_nodes.handle_consent,
    )

    workflow.add_node(
        "support_process",
        support_nodes.process_request,
    )

    workflow.add_node(
        "support_session_decision",
        support_nodes.handle_session_decision,
    )

    workflow.add_node(
        "support_confirm_session",
        support_nodes.confirm_session,
    )

    workflow.add_node(
        "support_alternative",
        support_nodes.propose_alternative,
    )

    # ---------------------------------
    # Newsletter temporaire
    # ---------------------------------

    workflow.add_node(
        "newsletter",
        newsletter_not_implemented,
    )

    # ---------------------------------
    # Point d'entrée
    # ---------------------------------

    workflow.add_conditional_edges(
        START,
        route_graph_entry,
        {
            "supervisor": "supervisor",
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
            "newsletter": "newsletter",
        },
    )

    # ---------------------------------
    # Routage du Supervisor
    # ---------------------------------

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "guide": "guide",
            "support_extract": (
                "support_extract"
            ),
            "newsletter": "newsletter",
            "clarification": (
                "clarification"
            ),
            "out_of_scope": (
                "out_of_scope"
            ),
        },
    )

    # ---------------------------------
    # Routage interne Support
    # ---------------------------------

    workflow.add_conditional_edges(
        "support_extract",
        route_after_extraction,
        {
            "missing": "support_missing",
            "consent": "support_missing",
            "process": "support_process",
            "end": END,
        },
    )

    workflow.add_edge(
        "support_missing",
        END,
    )

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

    # Ces nodes produisent directement une
    # réponse finale.
    workflow.add_edge(
        "support_process",
        END,
    )

    workflow.add_edge(
        "support_confirm_session",
        END,
    )

    workflow.add_edge(
        "support_alternative",
        END,
    )

    # ---------------------------------
    # Fin des autres workflows
    # ---------------------------------

    workflow.add_edge(
        "guide",
        END,
    )

    workflow.add_edge(
        "clarification",
        END,
    )

    workflow.add_edge(
        "out_of_scope",
        END,
    )

    workflow.add_edge(
        "newsletter",
        END,
    )

    return workflow.compile(
        checkpointer=InMemorySaver(),
    )