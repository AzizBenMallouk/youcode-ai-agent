from functools import lru_cache

from langchain_core.embeddings import (
    Embeddings,
)
from langchain_core.language_models import (
    BaseChatModel,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_ollama import (
    ChatOllama,
    OllamaEmbeddings,
)

from youcode_ai.core.config import settings


@lru_cache(maxsize=1)
def create_chat_model() -> BaseChatModel:
    if settings.chat_provider == "gemini":
        if not settings.google_api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is required "
                "for Gemini chat."
            )

        return ChatGoogleGenerativeAI(
            model=settings.gemini_chat_model,
            google_api_key=(
                settings.google_api_key
            ),
            temperature=0,
            max_retries=1,
        )

    if settings.chat_provider == "ollama":
        return ChatOllama(
            model=settings.ollama_chat_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    raise ValueError(
        "Unsupported chat provider: "
        f"{settings.chat_provider}"
    )


@lru_cache(maxsize=1)
def create_embedding_model() -> Embeddings:
    if (
        settings.embedding_provider
        == "gemini"
    ):
        if not settings.google_api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is required "
                "for Gemini embeddings."
            )

        return GoogleGenerativeAIEmbeddings(
            model=(
                settings
                .gemini_embedding_model
            ),
            google_api_key=(
                settings.google_api_key
            ),
        )

    if (
        settings.embedding_provider
        == "ollama"
    ):
        return OllamaEmbeddings(
            model=(
                settings
                .ollama_embedding_model
            ),
            base_url=(
                settings.ollama_base_url
            ),
        )

    raise ValueError(
        "Unsupported embedding provider: "
        f"{settings.embedding_provider}"
    )