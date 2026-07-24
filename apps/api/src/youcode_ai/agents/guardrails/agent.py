from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from youcode_ai.agents.guardrails.prompt import GUARDRAIL_SYSTEM_PROMPT
from youcode_ai.agents.guardrails.schemas import GuardrailResult
from youcode_ai.core.llm import create_chat_model


def create_guardrail_agent() -> Runnable:
    llm = create_chat_model()
    structured_llm = llm.with_structured_output(GuardrailResult)

    prompt = ChatPromptTemplate.from_messages(
        [("system", GUARDRAIL_SYSTEM_PROMPT), ("human", "{message}")]
    )

    return prompt | structured_llm
