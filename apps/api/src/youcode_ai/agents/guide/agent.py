from functools import lru_cache

from langchain.agents import create_agent
from langchain.agents.structured_output import (
    ToolStrategy,
)
from langgraph.graph.state import CompiledStateGraph

from youcode_ai.agents.guide.prompt import (
    GUIDE_AGENT_SYSTEM_PROMPT,
)
from youcode_ai.agents.guide.schemas import (
    GuideResponse,
)
from youcode_ai.agents.guide.tools import (
    search_youcode_knowledge,
)
from youcode_ai.core.llm import (
    create_chat_model,
)


@lru_cache(maxsize=1)
def create_guide_agent(
) -> CompiledStateGraph:
    """
    Crée le Guide Agent de YouCode.

    L'agent peut :
    - comprendre la question du visiteur ;
    - appeler le moteur RAG ;
    - analyser les documents officiels ;
    - générer une réponse structurée.
    """

    return create_agent(
        model=create_chat_model(),
        tools=[
            search_youcode_knowledge,
        ],
        system_prompt=(
            GUIDE_AGENT_SYSTEM_PROMPT
        ),
        response_format=ToolStrategy(
            GuideResponse
        ),
        name="youcode_guide_agent",
    )