from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from shared.core.config import settings


@lru_cache(maxsize=2)
def create_chat_model(*, use_cache: bool = True) -> BaseChatModel:
    """
    Create a chat model via the LiteLLM proxy.

    Args:
        use_cache: If True (default), allow LiteLLM to use the semantic
                   cache (Qdrant) for this model's requests.
                   If False, send the 'no-cache' directive so LiteLLM
                   always forwards to the LLM provider.

    Only the Guide agent should use cache (stable FAQ answers).
    All other agents (Orchestrator, Support, Newsletter, Admin)
    must set use_cache=False because their data is unique per user.
    """
    headers: dict = {}
    if not use_cache or not settings.semantic_cache_enabled:
        headers = {"no-cache": "True"}

    return ChatOpenAI(
        model=settings.litellm_chat_model,
        base_url=settings.litellm_url,
        api_key="sk-litellm",  # LiteLLM manages the real provider API keys
        temperature=0,
        max_retries=1,
        default_headers=headers,
    )


@lru_cache(maxsize=1)
def create_embedding_model() -> Embeddings:
    """
    Create an embedding model via the LiteLLM proxy.

    Routes through LiteLLM so the embedding provider can be changed
    in litellm_config.yaml without modifying Python code.
    The model name must match a model_name entry in litellm_config.yaml.
    """
    return OpenAIEmbeddings(
        model=settings.litellm_embedding_model,
        base_url=settings.litellm_url,
        api_key="sk-litellm",  # LiteLLM manages the real provider API keys
        check_embedding_ctx_length=False,
    )
