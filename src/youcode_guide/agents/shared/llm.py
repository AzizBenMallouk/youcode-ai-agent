from functools import lru_cache

from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)
from langchain_ollama import ChatOllama

from youcode_guide.config import settings


@lru_cache(maxsize=1)
def create_chat_model() -> BaseChatModel:
    if settings.chat_provider == "gemini":
        return create_gemini_chat_model()

    if settings.chat_provider == "ollama":
        return create_ollama_chat_model()

    raise ValueError(
        "Unsupported chat provider: "
        f"{settings.chat_provider}"
    )


def create_gemini_chat_model(
) -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY is required "
            "when CHAT_PROVIDER=gemini."
        )

    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=(
            settings.google_api_key
        ),
        temperature=0,
        max_retries=2,
    )


def create_ollama_chat_model(
) -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_chat_model,
        base_url=settings.ollama_base_url,
        temperature=0,
    )