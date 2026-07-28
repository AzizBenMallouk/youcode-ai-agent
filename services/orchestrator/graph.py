from typing import Literal
from langgraph.graph import StateGraph, START, END
from .state import OrchestratorState
from .supervisor.nodes import create_supervisor_nodes
from .guardrail.nodes import create_guardrail_nodes

GuardrailRoute = Literal["supervisor", "guardrail_refusal"]

def route_after_guardrail(state: OrchestratorState) -> GuardrailRoute:
    active_agent = state.get("active_agent")
    if active_agent == "guardrail_refusal":
        return "guardrail_refusal"
    return "supervisor"

def route_after_supervisor(state: OrchestratorState) -> Literal["supervisor_clarification", "supervisor_out_of_scope", "end"]:
    route = state.get("route")
    if route == "clarification":
        return "supervisor_clarification"
    if route == "out_of_scope":
        return "supervisor_out_of_scope"
    return "end"

def create_graph(checkpointer=None):
    builder = StateGraph(OrchestratorState)
    
    supervisor_nodes = create_supervisor_nodes()
    guardrail_nodes = create_guardrail_nodes()
    
    # Add nodes
    builder.add_node("guardrail_verify", guardrail_nodes.verify_message)
    builder.add_node("guardrail_refusal", guardrail_nodes.refusal)
    
    builder.add_node("supervisor_route", supervisor_nodes.route_message)
    builder.add_node("supervisor_clarification", supervisor_nodes.clarification)
    builder.add_node("supervisor_out_of_scope", supervisor_nodes.out_of_scope)
    
    # Entry point
    builder.add_edge(START, "guardrail_verify")
    
    # Routing
    builder.add_conditional_edges(
        "guardrail_verify",
        route_after_guardrail,
        {
            "supervisor": "supervisor_route",
            "guardrail_refusal": "guardrail_refusal",
        },
    )
    
    builder.add_edge("guardrail_refusal", END)
    
    # Supervisor logic
    builder.add_conditional_edges(
        "supervisor_route",
        route_after_supervisor,
        {
            "supervisor_clarification": "supervisor_clarification",
            "supervisor_out_of_scope": "supervisor_out_of_scope",
            "end": END,
        },
    )
    
    builder.add_edge("supervisor_clarification", END)
    builder.add_edge("supervisor_out_of_scope", END)
    
    return builder.compile(checkpointer=checkpointer)
