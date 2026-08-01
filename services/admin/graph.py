from langgraph.graph import END, StateGraph
from .nodes import AdminNodes
from .state import AdminState
from .agent import create_admin_agent

def create_graph(checkpointer=None) -> StateGraph:
    """Crée le graphe pour l'Agent Admin."""

    nodes = AdminNodes()
    agent = create_admin_agent()
    workflow = StateGraph(AdminState)

    workflow.add_node("check_guardrails", nodes.check_guardrails)
    workflow.add_node("agent", agent)

    workflow.set_entry_point("check_guardrails")

    def route_guardrails(state: AdminState) -> str:
        if state.get("admin_phase") == "rejected":
            return END
        return "agent"

    workflow.add_conditional_edges("check_guardrails", route_guardrails)
    workflow.add_edge("agent", END)

    return workflow.compile(checkpointer=checkpointer)
