import os
from dotenv import load_dotenv
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL")

    ollama_chat_model: str = os.getenv("OLLAMA_CHAT_MODEL")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL")

    qdrant_url: str = os.getenv("QDRANT_URL")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION")

    documents_path: Path = Path(os.getenv("DOCUMENTS_PATH"))

    retrieval_k: int = Field(
        default=os.getenv("RETRIEVAL_K"),
        ge=1,
        le=20,
    )

    chunk_size: int = Field(
        default=os.getenv("CHUNK_SIZE"),
        ge=100,
        le=5000,
    )

    chunk_overlap: int = Field(
        default=os.getenv("CHUNK_OVERLAP"),
        ge=0,
        le=1000,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()