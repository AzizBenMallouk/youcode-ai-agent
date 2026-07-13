from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from youcode_ai_guide.config import (
    Settings,
    get_settings,
)
from youcode_ai_guide.models import GuideResponse
from youcode_ai_guide.prompts import create_rag_prompt, create_contextualize_prompt
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

        self.contextualize_prompt = (
            create_contextualize_prompt()
        )

        self.contextualize_chain = (
            self.contextualize_prompt
            | self.chat_model
            | StrOutputParser()
        )

        self.rag_prompt = create_rag_prompt()

        self.rag_chain = (
            self.rag_prompt
            | self.structured_model
        )

        self.history: list[
            tuple[str, str]
        ] = []

    def format_history(self) -> str:
        if not self.history:
            return "Aucun historique."

        recent_history = self.history[-3:]

        lines: list[str] = []

        for user_message, assistant_message in recent_history:
            lines.append(
                f"Visiteur : {user_message}"
            )

            lines.append(
                f"Assistant : {assistant_message}"
            )

        return "\n".join(lines)
    

    def contextualize_question(
        self,
        question: str,
    ) -> str:
        if not self.history:
            return question

        standalone_question = (
            self.contextualize_chain.invoke(
                {
                    "chat_history": (
                        self.format_history()
                    ),
                    "question": question,
                }
            )
        )

        standalone_question = (
            standalone_question.strip()
        )

        if not standalone_question:
            return question

        return standalone_question

    def ask(
        self,
        question: str,
    ) -> GuideResponse:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError(
                "La question ne peut pas être vide."
            )

        chat_history = self.format_history()

        # Transformer une question comme
        # "mais comment ?" en question autonome
        standalone_question = (
            self.contextualize_question(
                clean_question
            )
        )

        print(
            "[Question recherchée] "
            f"{standalone_question}"
        )

        # Utiliser la question reformulée
        # pour la recherche Qdrant
        search_results = search_documents(
            question=standalone_question,
            vector_store=self.vector_store,
            k=self.settings.retrieval_k
        )

        documents = [
            document
            for document, _score in search_results
        ]

        context = format_context(documents)

        # Donner au modèle :
        # - l'historique ;
        # - le contexte récupéré ;
        # - la question originale.
        response = self.rag_chain.invoke(
            {
                "chat_history": chat_history,
                "context": context,
                "question": clean_question,
            }
        )

        # Enregistrer le nouvel échange
        self.history.append(
            (
                clean_question,
                response.answer,
            )
        )

        # Limiter la mémoire
        self.history = self.history[-3:]

        return response
    
    def clear_history(self) -> None:
        self.history.clear()

