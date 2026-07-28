from functools import lru_cache
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langgraph.graph.state import CompiledStateGraph
from .prompt import GUIDE_AGENT_SYSTEM_PROMPT
from .schemas import GuideResponse
from .tools import create_guide_tools
from shared.core.llm import create_chat_model

@lru_cache(maxsize=1)
def create_guide_agent() -> CompiledStateGraph:
    return create_agent(
        model=create_chat_model(),
        tools=create_guide_tools(),
        system_prompt=GUIDE_AGENT_SYSTEM_PROMPT,
        response_format=ToolStrategy(GuideResponse),
        name="youcode_guide_agent",
    )
