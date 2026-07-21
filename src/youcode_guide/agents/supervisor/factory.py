from langchain_core.prompts import (
    ChatPromptTemplate,
)
from langchain_core.messages import (
    HumanMessage, SystemMessage
)
from langchain_core.runnables import (
    Runnable,
)

from youcode_guide.agents.shared.llm import (
    create_chat_model,
)
from youcode_guide.agents.supervisor.models import (
    SupervisorDecision,
)
from youcode_guide.agents.supervisor.prompt import (
    SUPERVISOR_SYSTEM_PROMPT,
)


def create_supervisor_agent(
) -> Runnable:
    prompt = (
        ChatPromptTemplate
        .from_messages(
            [
                SystemMessage(
                    content=SUPERVISOR_SYSTEM_PROMPT,
                ),
                HumanMessage(
                    content="{message}"
                )
            ]
        )
    )

    model = create_chat_model()

    structured_model = (
        model.with_structured_output(
            SupervisorDecision
        )
    )

    return (
        prompt
        | structured_model
    )