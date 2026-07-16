from langchain_ollama import OllamaEmbeddings

from youcode_ai_guide.config import Settings


def create_embeddings(
    settings: Settings,
) -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )