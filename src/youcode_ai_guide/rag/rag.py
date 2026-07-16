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
    create_mmr_retriever,
    retrieve_documents,
)
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
)

from youcode_ai_guide.memory import (
    get_session_history,
)


def package_guide_response(
    response: GuideResponse,
) -> dict:
    return {
        "response": response,
        "message": AIMessage(
            content=response.answer
        ),
    }

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



        self.retriever = create_mmr_retriever(
            self.vector_store, 
            self.settings.retrieval_k,
            self.settings.fetch_k,
            self.settings.lambda_mult
        )

        self.prepare_rag_input = (
            RunnablePassthrough.assign(
                context=(
                    RunnableLambda(
                        lambda data: (
                            data["search_question"]
                        )
                    )
                    | self.retriever
                    | RunnableLambda(
                        format_context
                    )
                )
            )
        )

        self.rag_prompt = create_rag_prompt()

        self.rag_chain = (
            self.prepare_rag_input
            | self.rag_prompt
            | self.structured_model
            | RunnableLambda(
                package_guide_response
            )
        )

        self.rag_chain_with_history = (
            RunnableWithMessageHistory(
                self.rag_chain,
                get_session_history,
                input_messages_key="question",
                history_messages_key=(
                    "chat_history"
                ),
                output_messages_key="message",
            )
        )

    # def format_history(self) -> str:
    #     if not self.history:
    #         return "Aucun historique."

    #     recent_history = self.history[-3:]

    #     lines: list[str] = []

    #     for user_message, assistant_message in recent_history:
    #         lines.append(
    #             f"Visiteur : {user_message}"
    #         )

    #         lines.append(
    #             f"Assistant : {assistant_message}"
    #         )

    #     return "\n".join(lines)
    

    def contextualize_question(
        self,
        session_id: str,
        question: str,
    ) -> str:
        
        history = get_session_history(
            session_id
        )


        if not history.messages:
            return question

        standalone_question = (
            self.contextualize_chain.invoke(
                {
                    "chat_history": history.messages,
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
        session_id: str,
        question: str,
    ) -> GuideResponse:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError(
                "La question ne peut pas être vide."
            )

        standalone_question = (
            self.contextualize_question(
                session_id, clean_question
            )
        )

        # print(
        #     "[Question recherchée] "
        #     f"{standalone_question}"
        # )

        # Utiliser la question reformulée
        # pour la recherche Qdrant
        # search_results = search_documents(
        #     question=standalone_question,
        #     vector_store=self.vector_store,
        #     k=self.settings.retrieval_k
        # )

        # retriever = create_threshold_retriever(
        #     self.vector_store, 
        #     self.settings.retrieval_k,
        #     self.settings.score_threshold
        # )

        # search_results = retrieve_documents(question, retriever)


        # documents = retrieve_documents(standalone_question, self.retriever)

        # context = format_context(documents)

        # # Donner au modèle :
        # # - l'historique ;
        # # - le contexte récupéré ;
        # # - la question originale.
        # response = self.rag_chain.invoke(
        #     {
        #         "chat_history": self.history,
        #         "context": context,
        #         "question": clean_question,
        #     }
        # )

        # # Enregistrer le nouvel échange
        # self.history.append(
        #     HumanMessage(
        #         content=clean_question
        #     )
        # )
        # self.history.append(
        #     AIMessage(
        #         content=response.answer
        #     )
        # )

        # # Limiter la mémoire
        # self.history = self.history[-5:]

        result = (
            self.rag_chain_with_history.invoke(
                {
                    "question": clean_question,
                    "search_question": (
                        standalone_question
                    ),
                },
                config={
                    "configurable": {
                        "session_id": session_id,
                    }
                },
            )
        )



        return result["response"]
    
    def clear_history(self) -> None:
        self.history.clear()

