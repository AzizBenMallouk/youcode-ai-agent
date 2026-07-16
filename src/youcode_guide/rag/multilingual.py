from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

from youcode_guide.llm import create_chat_model
from youcode_guide.models import (
    ContextualizedQuestion,
)
from youcode_guide.rag.prompts import (
    create_contextualize_prompt,
)


class QueryContextualizer:
    def __init__(
        self,
        chain: Runnable,
    ) -> None:
        self.chain = chain

    def contextualize(
        self,
        question: str,
        chat_history: list[BaseMessage],
    ) -> ContextualizedQuestion:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError(
                "The question cannot be empty."
            )

        result = self.chain.invoke(
            {
                "question": clean_question,
                "chat_history": chat_history,
            }
        )

        return ContextualizedQuestion.model_validate(
            result
        )


def create_query_contextualizer(
) -> QueryContextualizer:
    chat_model = create_chat_model()

    structured_model = (
        chat_model.with_structured_output(
            ContextualizedQuestion
        )
    )

    chain = (
        create_contextualize_prompt()
        | structured_model
    )

    return QueryContextualizer(chain)