from dataclasses import dataclass

from youcode_guide.config import settings
from youcode_guide.conversations.memory import (
    ConversationMemory,
)
from youcode_guide.models import (
    KnowledgeResult,
)
from youcode_guide.rag.multilingual import (
    QueryContextualizer,
    create_query_contextualizer,
)
from youcode_guide.rag.service import (
    RAGService,
    create_rag_service,
)


@dataclass
class ConversationalResult:
    search_question: str
    knowledge: KnowledgeResult


class ConversationalRAGService:
    def __init__(
        self,
        rag_service: RAGService,
        contextualizer: QueryContextualizer,
        memory: ConversationMemory,
    ) -> None:
        self.rag_service = rag_service
        self.contextualizer = contextualizer
        self.memory = memory

    def ask(
        self,
        session_id: str,
        question: str,
    ) -> ConversationalResult:
        history = self.memory.get_messages(
            session_id
        )

        contextualized = (
            self.contextualizer.contextualize(
                question=question,
                chat_history=history,
            )
        )

        result = self.rag_service.ask(
            question=question,
            search_question=(
                contextualized.search_question
            ),
            chat_history=history,
        )

        self.memory.add_turn(
            session_id=session_id,
            human_content=question,
            ai_content=result.response.answer,
        )

        return ConversationalResult(
            search_question=(
                contextualized.search_question
            ),
            knowledge=result,
        )

    def clear_session(
        self,
        session_id: str,
    ) -> None:
        self.memory.clear(session_id)


def create_conversational_rag_service(
) -> ConversationalRAGService:
    return ConversationalRAGService(
        rag_service=create_rag_service(),
        contextualizer=(
            create_query_contextualizer()
        ),
        memory=ConversationMemory(
            max_messages=(
                settings.max_history_messages
            )
        ),
    )