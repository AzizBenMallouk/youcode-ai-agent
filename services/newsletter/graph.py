from typing import Literal
from langgraph.graph import StateGraph, START, END
from .state import NewsletterState
from .nodes import create_newsletter_nodes

ExtractionRoute = Literal["newsletter_process", "awaiting_consent", "end"]
ConsentRoute = Literal["newsletter_process", "end"]

def route_after_newsletter_extraction(state: NewsletterState) -> ExtractionRoute:
    newsletter_phase = state.get("newsletter_phase")
    if newsletter_phase in ["collecting", "cancelled", "completed"]:
        return "end"
    if newsletter_phase == "awaiting_consent":
        return "awaiting_consent"
    if newsletter_phase == "processing" and state.get("newsletter_consent_confirmed", False):
        return "newsletter_process"
    return "end"

def route_after_newsletter_consent(state: NewsletterState) -> ConsentRoute:
    if state.get("newsletter_consent_confirmed", False):
        return "newsletter_process"
    return "end"

def create_graph(checkpointer=None):
    builder = StateGraph(NewsletterState)
    newsletter_nodes = create_newsletter_nodes()
    
    # Add nodes
    builder.add_node("newsletter_extract", newsletter_nodes.extract)
    builder.add_node("newsletter_consent", newsletter_nodes.consent)
    builder.add_node("newsletter_process", newsletter_nodes.process)
    
    # Entry point
    builder.add_edge(START, "newsletter_extract")
    
    # Routing
    builder.add_conditional_edges(
        "newsletter_extract",
        route_after_newsletter_extraction,
        {
            "newsletter_process": "newsletter_process",
            "awaiting_consent": "newsletter_consent",
            "end": END,
        },
    )
    
    builder.add_conditional_edges(
        "newsletter_consent",
        route_after_newsletter_consent,
        {
            "newsletter_process": "newsletter_process",
            "end": END,
        },
    )
    
    builder.add_edge("newsletter_process", END)
    
    return builder.compile(checkpointer=checkpointer)
