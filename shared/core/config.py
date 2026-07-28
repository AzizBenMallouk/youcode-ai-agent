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

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
        "grok",
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

    # Grok
    grok_api_key: str | None = None
    grok_chat_model: str = "grok-2-latest"

    # LangGraph
    langgraph_checkpoint_path: str

    # Database
    database_url: str

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str | None = None
    qdrant_documents_collection: str = Field(default="youcode_documents_gemini")
    qdrant_knowledge_gaps_collection: str = Field(
        default="youcode_knowledge_gaps_gemini"
    )
    qdrant_guardrails_collection: str = Field(default="youcode_guardrails_gemini")
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
        default=0.7,
        ge=0.0,
        le=1.0,
    )
    rag_use_reranking: bool = Field(default=True)
    rag_rerank_top_k: int = Field(default=5, gt=0)

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
    orchestrator_url: str = Field(default="http://orchestrator:8010")
    guide_url: str = Field(default="http://guide:8001")
    support_url: str = Field(default="http://support:8002")
    newsletter_url: str = Field(default="http://newsletter:8003")
    evolution_api_url: str = Field(default="http://evolution-api:8080")
    evolution_api_key: str = Field(default="super_secret_key")
    webhook_secret: str = Field(default="")

    registration_api_url: str
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

    # Email
    email_provider: str = "console"
    email_from_address: str = "no-reply@youcode.ma"
    email_from_name: str = "YouCode"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_timeout: int = 10
    email_max_attempts: int = 3

    # Fast API
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Auth
    auth_secret_key: str = Field(
        min_length=32, default="replace-with-a-secure-random-key-at-least-32-chars"
    )
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"
    auth_max_login_attempts: int = 5
    auth_lockout_minutes: int = 15
    admin_initial_email: str = ""
    admin_initial_password: str = ""

    @model_validator(mode="after")
    def validate_provider_configuration(
        self,
    ) -> "Settings":
        uses_gemini = (
            self.chat_provider == "gemini" or self.embedding_provider == "gemini"
        )

        if uses_gemini and not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when "
                "Gemini is used as chat or "
                "embedding provider."
            )

        if self.chat_provider == "grok" and not self.grok_api_key:
            raise ValueError(
                "GROK_API_KEY is required when Grok is used as chat provider."
            )

        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()

    if not settings.documents_path.is_absolute():
        settings.documents_path = PROJECT_ROOT / settings.documents_path

    if not settings.parent_store_path.is_absolute():
        settings.parent_store_path = PROJECT_ROOT / settings.parent_store_path

    if not Path(settings.langgraph_checkpoint_path).is_absolute():
        settings.langgraph_checkpoint_path = str(PROJECT_ROOT / settings.langgraph_checkpoint_path)

    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url[10:]
        if not Path(db_path).is_absolute():
            abs_db_path = PROJECT_ROOT / db_path
            settings.database_url = f"sqlite:///{abs_db_path}"

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
