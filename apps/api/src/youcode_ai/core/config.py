from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import (
    Field,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[5]
)

ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str
    app_env: Literal[
        "development",
        "test",
        "production",
    ]
    app_debug: bool

    # Providers
    chat_provider: Literal[
        "gemini",
        "ollama",
    ]

    embedding_provider: Literal[
        "gemini",
        "ollama",
    ]

    # Gemini
    google_api_key: str | None = None
    gemini_chat_model: str
    gemini_embedding_model: str

    # Ollama
    ollama_base_url: str
    ollama_chat_model: str
    ollama_embedding_model: str

    # Database
    database_url: str

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_documents_collection: str
    qdrant_knowledge_gaps_collection: str
    rag_ingestion_batch_size: int = Field(
        ge=1,
        le=500,
    )

    # RAG
    documents_path: Path
    parent_store_path: Path

    rag_top_k: int = Field(
        ge=1,
        le=50,
    )

    rag_score_threshold: float = Field(
        ge=0,
        le=1,
    )

    rag_parent_chunk_size: int = Field(
        ge=500,
        le=5000,
    )

    rag_parent_chunk_overlap: int = Field(
        ge=0,
        le=1000,
    )

    rag_child_chunk_size: int = Field(
        ge=100,
        le=2000,
    )

    rag_child_chunk_overlap: int = Field(
        ge=0,
        le=500,
    )

    # External services
    registration_api_url: str
    registration_api_timeout: float = 10.0
    registration_api_key: str | None = None

    test_session_api_url: str

    email_api_url: str


    external_api_timeout: float = Field(
        gt=0,
        le=120,
    )

    # Conversation
    max_history_messages: int = Field(
        ge=1,
        le=100,
    )

    # Consent
    consent_version: str
    consent_secret_key: str = Field(
        min_length=32,
    )

    consent_token_ttl_minutes: int = Field(
        ge=1,
        le=1440,
    )

    # Fast API
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @model_validator(mode="after")
    def validate_provider_configuration(
        self,
    ) -> "Settings":
        uses_gemini = (
            self.chat_provider == "gemini"
            or self.embedding_provider
            == "gemini"
        )

        if (
            uses_gemini
            and not self.google_api_key
        ):
            raise ValueError(
                "GOOGLE_API_KEY is required when "
                "Gemini is used as chat or "
                "embedding provider."
            )

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()

    settings.documents_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.parent_store_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return settings


settings = get_settings()