from langchain_core.documents import Document
from langchain_ollama import ChatOllama

from youcode_ai_guide.config import (
    Settings,
    get_settings,
)
from youcode_ai_guide.models import GuideResponse
from youcode_ai_guide.prompts import create_rag_prompt
from youcode_ai_guide.retriever import (
    create_retriever_store,
    search_documents,
)


def create_chat_model(
    settings: Settings,
) -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=0,
    )


def format_context(
    documents: list[Document],
) -> str:
    if not documents:
        return (
            "Aucune information officielle pertinente "
            "n'a été trouvée."
        )

    formatted_documents: list[str] = []

    for index, document in enumerate(
        documents,
        start=1,
    ):
        file_name = document.metadata.get(
            "file_name",
            "source inconnue",
        )

        page = document.metadata.get("page")

        source_information = (
            f"Source {index}: {file_name}"
        )

        if page is not None:
            source_information += (
                f", page {page + 1}"
            )

        formatted_document = (
            f"--- DÉBUT SOURCE {index} ---\n"
            f"{source_information}\n\n"
            f"{document.page_content}\n"
            f"--- FIN SOURCE {index} ---"
        )

        formatted_documents.append(
            formatted_document
        )

    return "\n\n".join(formatted_documents)


class YouCodeRAG:
    def __init__(self) -> None:
        self.settings = get_settings()

        self.vector_store = create_retriever_store(
            self.settings
        )

        self.chat_model = create_chat_model(
            self.settings
        )

        self.structured_model = (
            self.chat_model.with_structured_output(
                GuideResponse,
                method="json_schema",
            )
        )

        self.prompt = create_rag_prompt()

        self.chain = (
            self.prompt
            | self.structured_model
        )

    def ask(
        self,
        question: str,
    ) -> GuideResponse:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError(
                "La question ne peut pas être vide."
            )

        search_results = search_documents(
            question=clean_question,
            vector_store=self.vector_store,
            k=self.settings.retrieval_k
        )

        documents = [
            document
            for document, _score in search_results
        ]

        context = format_context(documents)

        response = self.chain.invoke(
            {
                "question": clean_question,
                "context": context,
            }
        )

        return response