import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"La variable d'environnement {name} est absente."
        )

    return value


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str
    ollama_chat_model: str
    ollama_embedding_model: str

    qdrant_url: str
    qdrant_collection: str

    database_url: str
    documents_path: str


def load_settings() -> Settings:
    return Settings(
        ollama_base_url=get_required_env(
            "OLLAMA_BASE_URL"
        ),
        ollama_chat_model=get_required_env(
            "OLLAMA_CHAT_MODEL"
        ),
        ollama_embedding_model=get_required_env(
            "OLLAMA_EMBEDDING_MODEL"
        ),
        qdrant_url=get_required_env(
            "QDRANT_URL"
        ),
        qdrant_collection=get_required_env(
            "QDRANT_COLLECTION"
        ),
        database_url=get_required_env(
            "DATABASE_URL"
        ),
        documents_path=get_required_env(
            "DOCUMENTS_PATH"
        ),
    )


settings = load_settings()