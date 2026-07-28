from typing import Literal
from langgraph.graph import StateGraph, START, END
from .state import SupportState
from .nodes import create_support_nodes

def route_after_extraction(state: SupportState) -> Literal["missing", "consent", "process", "end"]:
    support_phase = state.get("support_phase")
    if support_phase == "collecting":
        return "missing"
    if support_phase == "awaiting_consent":
        return "consent"
    if support_phase == "processing" and state.get("consent_confirmed", False):
        return "process"
    return "end"

def route_support_entry(state: SupportState) -> Literal["support_extract", "support_consent", "support_process", "support_session_decision", "support_confirm_session", "support_alternative", "end"]:
    support_phase = state.get("support_phase", "collecting")
    if support_phase == "collecting":
        return "support_extract"
    if support_phase == "awaiting_consent":
        return "support_consent"
    if support_phase == "processing":
        return "support_process"
    if support_phase == "awaiting_session_confirmation":
        return "support_session_decision"
    if support_phase == "confirming_session":
        return "support_confirm_session"
    if support_phase == "searching_alternative":
        return "support_alternative"
    return "end"

def route_after_consent(state: SupportState) -> Literal["support_process", "end"]:
    support_phase = state.get("support_phase")
    consent_confirmed = state.get("consent_confirmed", False)
    if support_phase == "processing" and consent_confirmed:
        return "support_process"
    return "end"

def route_after_session_decision(state: SupportState) -> Literal["support_confirm_session", "support_alternative", "end"]:
    support_phase = state.get("support_phase")
    if support_phase == "confirming_session":
        return "support_confirm_session"
    if support_phase == "searching_alternative":
        return "support_alternative"
    return "end"

def create_graph(checkpointer=None):
    builder = StateGraph(SupportState)
    support_nodes = create_support_nodes()
    
    # Add nodes
    builder.add_node("support_extract", support_nodes.extract_information)
    builder.add_node("support_missing", support_nodes.request_missing_information)
    builder.add_node("support_consent", support_nodes.classify_consent)
    builder.add_node("support_process", support_nodes.process_request)
    builder.add_node("support_session_decision", support_nodes.classify_session_proposal)
    builder.add_node("support_confirm_session", support_nodes.confirm_session_proposal)
    builder.add_node("support_alternative", support_nodes.search_alternative_session)
    
    # Entry point routing instead of direct edge
    builder.add_conditional_edges(
        START,
        route_support_entry,
        {
            "support_extract": "support_extract",
            "support_consent": "support_consent",
            "support_process": "support_process",
            "support_session_decision": "support_session_decision",
            "support_confirm_session": "support_confirm_session",
            "support_alternative": "support_alternative",
            "end": END,
        },
    )
    
    # Routing
    builder.add_conditional_edges(
        "support_extract",
        route_after_extraction,
        {
            "missing": "support_missing",
            "consent": "support_consent",
            "process": "support_process",
            "end": END,
        },
    )
    
    builder.add_edge("support_missing", END)
    
    builder.add_conditional_edges(
        "support_consent",
        route_after_consent,
        {
            "support_process": "support_process",
            "end": END,
        },
    )
    
    builder.add_edge("support_process", "support_session_decision")
    
    builder.add_conditional_edges(
        "support_session_decision",
        route_after_session_decision,
        {
            "support_confirm_session": "support_confirm_session",
            "support_alternative": "support_alternative",
            "end": END,
        },
    )
    
    builder.add_edge("support_confirm_session", END)
    builder.add_edge("support_alternative", END)
    
    return builder.compile(checkpointer=checkpointer)
