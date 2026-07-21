from langchain.agents import create_agent

from youcode_guide.agents.rescheduling.models import (
    ReschedulingAgentResponse,
)
from youcode_guide.agents.rescheduling.prompt import (
    RESCHEDULING_AGENT_SYSTEM_PROMPT,
)
from youcode_guide.agents.rescheduling.tools import (
    create_rescheduling_tools,
)
from youcode_guide.agents.shared.llm import (
    create_chat_model,
)


def create_rescheduling_agent():
    return create_agent(
        model=create_chat_model(),
        tools=create_rescheduling_tools(),
        system_prompt=(
            RESCHEDULING_AGENT_SYSTEM_PROMPT
        ),
        response_format=(
            ReschedulingAgentResponse
        ),
    )