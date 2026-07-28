from langgraph.graph import StateGraph, START, END
from .state import GuideState
from .nodes import create_guide_nodes

def create_graph(checkpointer=None):
    builder = StateGraph(GuideState)
    guide_nodes = create_guide_nodes()
    
    builder.add_node("guide", guide_nodes.answer_question)
    builder.add_edge(START, "guide")
    builder.add_edge("guide", END)
    
    return builder.compile(checkpointer=checkpointer)
