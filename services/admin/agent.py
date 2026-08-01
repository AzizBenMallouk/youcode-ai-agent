from functools import lru_cache
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from shared.core.llm import create_chat_model
from .prompt import ADMIN_SYSTEM_PROMPT
from .tools import get_visitor_requests, generate_report_via_mcp

@lru_cache(maxsize=1)
def create_admin_agent() -> CompiledStateGraph:
    return create_react_agent(
        model=create_chat_model(),
        tools=[get_visitor_requests, generate_report_via_mcp],
        prompt=ADMIN_SYSTEM_PROMPT
    )
