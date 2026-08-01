from functools import lru_cache

from langchain_core.embeddings import (
    Embeddings,
)
from langchain_core.language_models import (
    BaseChatModel,
)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from shared.core.config import settings


@lru_cache(maxsize=1)
def create_chat_model() -> BaseChatModel:
    if settings.chat_provider == "litellm":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.litellm_chat_model,
            base_url=settings.litellm_url,
            api_key="sk-litellm",
            temperature=0,
            max_retries=1,
        )

    raise ValueError(f"Unsupported chat provider: {settings.chat_provider}")

    raise ValueError(f"Unsupported chat provider: {settings.chat_provider}")


@lru_cache(maxsize=1)
def create_embedding_model() -> Embeddings:
    if settings.embedding_provider == "gemini":
        if not settings.google_api_key or settings.google_api_key == "dummy_google_api_key":
            raise RuntimeError("GOOGLE_API_KEY is required for Gemini embeddings.")

        return GoogleGenerativeAIEmbeddings(
            model=(settings.gemini_embedding_model),
            google_api_key=(settings.google_api_key),
        )

    if settings.embedding_provider == "ollama":
        return OllamaEmbeddings(
            model=(settings.ollama_embedding_model),
            base_url=(settings.ollama_base_url),
        )

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
