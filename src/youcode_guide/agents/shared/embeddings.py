from functools import lru_cache

from langchain_core.embeddings import (
    Embeddings,
)
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
)
from langchain_ollama import (
    OllamaEmbeddings,
)

from youcode_guide.config import settings


@lru_cache(maxsize=1)
def create_embedding_model() -> Embeddings:
    if (
        settings.embedding_provider
        == "gemini"
    ):
        return create_gemini_embeddings()

    if (
        settings.embedding_provider
        == "ollama"
    ):
        return create_ollama_embeddings()

    raise ValueError(
        "Unsupported embedding provider: "
        f"{settings.embedding_provider}"
    )


def create_gemini_embeddings(
) -> GoogleGenerativeAIEmbeddings:
    if not settings.google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY is required "
            "when EMBEDDING_PROVIDER=gemini."
        )

    return GoogleGenerativeAIEmbeddings(
        model=(
            settings.gemini_embedding_model
        ),
        google_api_key=(
            settings.google_api_key
        ),
    )


def create_ollama_embeddings(
) -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=(
            settings.ollama_embedding_model
        ),
        base_url=settings.ollama_base_url,
    )