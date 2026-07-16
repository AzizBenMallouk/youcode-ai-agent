from langchain_core.runnables import Runnable

from youcode_guide.llm import create_chat_model
from youcode_guide.models import (
    GuideResponse,
    KnowledgeResult,
)
from youcode_guide.rag.context import (
    build_source_references,
    format_context,
)
from youcode_guide.rag.prompts import (
    create_rag_prompt,
)
from youcode_guide.rag.retriever import (
    ParentChildRetriever,
    create_parent_child_retriever,
)
from langchain_core.messages import BaseMessage


class RAGService:
    def __init__(
        self,
        retriever: ParentChildRetriever,
        rag_chain: Runnable,
    ) -> None:
        self.retriever = retriever
        self.rag_chain = rag_chain

    def ask(
        self,
        question: str,
        search_question: str | None = None,
        chat_history: list[BaseMessage] | None = None,
        ) -> KnowledgeResult:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError(
                "The question cannot be empty."
            )
        
        clean_search_question = (
            search_question.strip()
            if search_question
            else clean_question
        )

        
        history = chat_history or []

        retrieval_result = (
            self.retriever.search(
                clean_search_question
            )
        )

        context = format_context(
            retrieval_result.parents
        )

        raw_response = self.rag_chain.invoke(
            {
                "question": clean_question,
                "context": context,
                "chat_history": history,
            }
        )

        response = GuideResponse.model_validate(
            raw_response
        )

        # Sécurité déterministe :
        # aucun document = information indisponible
        if not retrieval_result.parents:
            response.information_available = False

        sources = build_source_references(
            retrieval_result.parents
        )

        return KnowledgeResult(
            response=response,
            sources=sources,
        )
    



def create_rag_service() -> RAGService:
    chat_model = create_chat_model()

    structured_model = (
        chat_model.with_structured_output(
            GuideResponse
        )
    )

    rag_chain = (
        create_rag_prompt()
        | structured_model
    )

    retriever = (
        create_parent_child_retriever()
    )

    return RAGService(
        retriever=retriever,
        rag_chain=rag_chain,
    )