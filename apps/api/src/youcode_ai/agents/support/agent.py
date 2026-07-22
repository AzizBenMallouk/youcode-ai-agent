from functools import lru_cache

from langchain.agents import (
    create_agent,
)

from youcode_ai.agents.support.context import (
    SupportAgentContext,
)
from youcode_ai.agents.support.prompt import (
    SUPPORT_AGENT_SYSTEM_PROMPT,
)
from youcode_ai.agents.support.tools import (
    create_support_tools,
)
from youcode_ai.core.llm import (
    create_chat_model,
)


@lru_cache(maxsize=1)
def create_support_agent():
    return create_agent(
        model=create_chat_model(),
        tools=create_support_tools(),
        system_prompt=(
            SUPPORT_AGENT_SYSTEM_PROMPT
        ),
        context_schema=(
            SupportAgentContext
        ),
    )