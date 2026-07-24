from functools import lru_cache

from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from youcode_ai.agents.guardrails.nodes import (
    create_guardrail_nodes,
)
from youcode_ai.agents.guide.nodes import (
    create_guide_nodes,
)
from youcode_ai.agents.newsletter.nodes import (
    create_newsletter_nodes,
)
from youcode_ai.agents.supervisor.nodes import (
    create_supervisor_nodes,
)
from youcode_ai.agents.support.nodes import (
    SupportNodes,
)
from youcode_ai.infrastructure.checkpoint.sqlite import (
    create_sqlite_checkpointer,
)
from youcode_ai.orchestration.routing import (
    route_after_consent,
    route_after_extraction,
    route_after_guardrail,
    route_after_newsletter_consent,
    route_after_newsletter_extraction,
    route_after_session_decision,
    route_after_supervisor,
)
from youcode_ai.orchestration.state import (
    YouCodeState,
)


@lru_cache(maxsize=1)
def create_youcode_graph():
    workflow = StateGraph(YouCodeState)

    supervisor_nodes = create_supervisor_nodes()

    guardrail_nodes = create_guardrail_nodes()

    guide_nodes = create_guide_nodes()

    support_nodes = SupportNodes()

    newsletter_nodes = create_newsletter_nodes()

    # ---------------------------------
    # Nodes Guardrails
    # ---------------------------------

    workflow.add_node(
        "input_guardrail",
        guardrail_nodes.verify_message,
    )

    workflow.add_node(
        "guardrail_refusal",
        guardrail_nodes.refusal,
    )

    # ---------------------------------
    # Nodes Supervisor
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
    # Node Guide
    # ---------------------------------

    workflow.add_node(
        "guide",
        guide_nodes.answer_question,
    )

    # ---------------------------------
    # Nodes Support
    # ---------------------------------

    workflow.add_node(
        "support_extract",
        support_nodes.extract_information,
    )

    workflow.add_node(
        "support_missing",
        support_nodes.request_missing_information,
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

    # ---------------------------------
    # Nodes Newsletter
    # ---------------------------------

    workflow.add_node(
        "newsletter_extract",
        newsletter_nodes.extract,
    )

    workflow.add_node(
        "newsletter_consent",
        newsletter_nodes.consent,
    )

    workflow.add_node(
        "newsletter_process",
        newsletter_nodes.process,
    )

    # ---------------------------------
    # Entrée globale
    # ---------------------------------

    workflow.add_edge(START, "input_guardrail")

    workflow.add_conditional_edges(
        "input_guardrail",
        route_after_guardrail,
        {
            "supervisor": "supervisor",
            "support_extract": ("support_extract"),
            "support_consent": ("support_consent"),
            "support_process": ("support_process"),
            "support_session_decision": ("support_session_decision"),
            "support_confirm_session": ("support_confirm_session"),
            "support_alternative": ("support_alternative"),
            "newsletter_extract": ("newsletter_extract"),
            "newsletter_consent": ("newsletter_consent"),
            "newsletter_process": ("newsletter_process"),
            "guardrail_refusal": "guardrail_refusal",
        },
    )

    workflow.add_edge("guardrail_refusal", END)

    # ---------------------------------
    # Routage Supervisor
    # ---------------------------------

    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "guide": "guide",
            "support_extract": ("support_extract"),
            "newsletter_extract": ("newsletter_extract"),
            "clarification": ("clarification"),
            "out_of_scope": ("out_of_scope"),
        },
    )

    # ---------------------------------
    # Workflow Support
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
            "support_process": ("support_process"),
            "end": END,
        },
    )

    workflow.add_edge(
        "support_process",
        END,
    )

    workflow.add_conditional_edges(
        "support_session_decision",
        route_after_session_decision,
        {
            "support_confirm_session": ("support_confirm_session"),
            "support_alternative": ("support_alternative"),
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

    # ---------------------------------
    # Workflow Newsletter
    # ---------------------------------

    workflow.add_conditional_edges(
        "newsletter_extract",
        route_after_newsletter_extraction,
        {
            "newsletter_process": ("newsletter_process"),
            "end": END,
        },
    )

    workflow.add_conditional_edges(
        "newsletter_consent",
        route_after_newsletter_consent,
        {
            "newsletter_process": ("newsletter_process"),
            "end": END,
        },
    )

    workflow.add_edge(
        "newsletter_process",
        END,
    )

    # ---------------------------------
    # Autres fins
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

    return workflow.compile(
        checkpointer=create_sqlite_checkpointer(),
    )
