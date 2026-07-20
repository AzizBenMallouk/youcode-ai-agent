from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from youcode_guide.agent.context import AgentRuntimeContext
from youcode_guide.agent.middlewares.handle_tool_errors import handle_tool_errors
from youcode_guide.agent.llm.prompt import (
    YOUCODE_AGENT_SYSTEM_PROMPT,
)
from youcode_guide.agent.llm.llm import create_chat_model
from youcode_guide.metier.models.guide_response import GuideResponse
from youcode_guide.agent.tools import create_youcode_tools


def create_youcode_agent():
    model = create_chat_model()
    tools = create_youcode_tools()
    checkpointer = InMemorySaver()

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=YOUCODE_AGENT_SYSTEM_PROMPT,
        context_schema=AgentRuntimeContext,
        response_format=GuideResponse.model_json_schema(),
        checkpointer=checkpointer,
        middleware=[handle_tool_errors],
    )