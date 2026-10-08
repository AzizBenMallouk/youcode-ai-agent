from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_name: str = Field(default="YouCode AI")
    app_env: Literal["development", "test", "production"] = Field(
        default="development"
    )
    app_debug: bool = Field(default=False)

    # -------------------------------------------------------------------------
    # LLM — all chat and embedding requests go through the LiteLLM proxy
    # -------------------------------------------------------------------------
    chat_provider: Literal["litellm"] = Field(default="litellm")
    litellm_url: str = Field(default="http://litellm:4000")
    litellm_chat_model: str = Field(default="gemini-3.5-flash-lite")
    litellm_embedding_model: str = Field(default="text-embedding-004")

    # Google API key — passed to LiteLLM via compose env, not used directly in Python
    google_api_key: str | None = Field(default=None)

    # -------------------------------------------------------------------------
    # Messaging — RabbitMQ
    # -------------------------------------------------------------------------
    rabbitmq_url: str = Field(default="amqp://guest:guest@rabbitmq:5672/")

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+psycopg2://youcode:youcode_pass@postgres:5432/evolution"
    )

    # -------------------------------------------------------------------------
    # LangGraph
    # -------------------------------------------------------------------------
    langgraph_checkpoint_path: str = Field(default="checkpoints.sqlite")

    # -------------------------------------------------------------------------
    # Semantic Cache (Guide agent only)
    # -------------------------------------------------------------------------
    semantic_cache_enabled: bool = Field(
        default=True,
        description="Enable LiteLLM semantic cache via Qdrant for the Guide agent",
    )
    semantic_cache_threshold: float = Field(
        default=0.95,
        ge=0.80,
        le=1.0,
        description="Cosine similarity threshold for a cache hit (0.95 = 95%)",
    )
    semantic_cache_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=604800,
        description="TTL in seconds for cached responses (default: 1 hour)",
    )
    semantic_cache_collection: str = Field(
        default="litellm_semantic_cache",
        description="Qdrant collection name for semantic cache vectors",
    )

    # -------------------------------------------------------------------------
    # Qdrant — Vector Store
    # -------------------------------------------------------------------------
    qdrant_url: str = Field(default="http://qdrant:6333")
    qdrant_api_key: str | None = None
    qdrant_documents_collection: str = Field(default="youcode_documents_gemini")
    qdrant_knowledge_gaps_collection: str = Field(
        default="youcode_knowledge_gaps_gemini"
    )
    qdrant_guardrails_collection: str = Field(default="youcode_guardrails_gemini")
    rag_ingestion_batch_size: int = Field(default=100, ge=1, le=500)

    # -------------------------------------------------------------------------
    # RAG — Retrieval-Augmented Generation
    # -------------------------------------------------------------------------
    documents_path: Path = Field(default=Path("documents"))
    parent_store_path: Path = Field(default=Path("parent_store"))

    rag_top_k: int = Field(default=5, ge=1, le=50)
    rag_score_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    rag_use_reranking: bool = Field(default=True)
    rag_rerank_top_k: int = Field(default=5, gt=0)

    rag_parent_chunk_size: int = Field(default=1000, ge=500, le=5000)
    rag_parent_chunk_overlap: int = Field(default=200, ge=0, le=1000)
    rag_child_chunk_size: int = Field(default=200, ge=100, le=2000)
    rag_child_chunk_overlap: int = Field(default=50, ge=0, le=500)

    # -------------------------------------------------------------------------
    # Memory — Conversation Summarizer
    # -------------------------------------------------------------------------
    max_history_messages: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Max messages kept in history before summarization triggers",
    )
    memory_summary_threshold: int = Field(
        default=30,
        ge=5,
        le=200,
        description="Number of messages that triggers automatic summarization",
    )
    memory_keep_recent: int = Field(
        default=10,
        ge=2,
        le=50,
        description="Number of recent messages to keep verbatim after summarization",
    )

    # -------------------------------------------------------------------------
    # External Services
    # -------------------------------------------------------------------------
    orchestrator_url: str = Field(default="http://orchestrator:8006")
    guide_url: str = Field(default="http://guide:8001")
    support_url: str = Field(default="http://support:8002")
    newsletter_url: str = Field(default="http://newsletter:8003")

    # WhatsApp / Evolution API
    evolution_api_url: str = Field(default="http://evolution-api:8080")
    evolution_api_key: str = Field(default="super_secret_key")
    webhook_secret: str = Field(default="")

    # YouCode external APIs
    registration_api_url: str = Field(default="http://registration-api:8080")
    registration_api_key: str | None = None
    test_session_api_url: str = Field(default="http://test-session-api:8080")
    email_api_url: str = Field(default="http://email-api:8080")
    external_api_timeout: float = Field(default=10.0, gt=0, le=120)

    # MCP Servers
    email_mcp_url: str = Field(default="http://email-mcp:8005")
    sheet_mcp_url: str = Field(default="http://sheet-gmcp:8004")

    # Admin notification
    admin_email: str = Field(
        default="admin@youcode.ma",
        description="Email address to notify when requires_human=True",
    )

    # Discord Gateway
    discord_bot_token: str = Field(default="")
    discord_channel_ids: str = Field(
        default="",
        description="Comma-separated list of Discord channel IDs to listen to",
    )

    # -------------------------------------------------------------------------
    # Consent
    # -------------------------------------------------------------------------
    consent_version: str = Field(default="1.0")
    consent_secret_key: str = Field(
        default="a-very-secret-consent-key-at-least-32-chars",
        min_length=32,
    )
    consent_token_ttl_minutes: int = Field(default=60, ge=1, le=1440)

    # -------------------------------------------------------------------------
    # Email (SMTP)
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # FastAPI / CORS
    # -------------------------------------------------------------------------
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # -------------------------------------------------------------------------
    # Auth
    # -------------------------------------------------------------------------
    auth_secret_key: str = Field(
        min_length=32,
        default="replace-with-a-secure-random-key-at-least-32-chars",
    )
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    auth_cookie_secure: bool = False
    auth_cookie_samesite: str = "lax"
    auth_max_login_attempts: int = 5
    auth_lockout_minutes: int = 15
    admin_initial_email: str = ""
    admin_initial_password: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()

    # HACK: GitOps helm charts hardcode DATABASE_URL to 'evolution'.
    # This conflicts with evolution-api's Prisma which expects an empty schema.
    # We force python microservices to connect to 'youcode_api' instead.
    if settings.database_url.endswith("/evolution"):
        settings.database_url = settings.database_url.replace("/evolution", "/youcode_api")

    if not settings.documents_path.is_absolute():
        settings.documents_path = PROJECT_ROOT / settings.documents_path

    if not settings.parent_store_path.is_absolute():
        settings.parent_store_path = PROJECT_ROOT / settings.parent_store_path

    if not Path(settings.langgraph_checkpoint_path).is_absolute():
        settings.langgraph_checkpoint_path = str(
            PROJECT_ROOT / settings.langgraph_checkpoint_path
        )

    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url[10:]
        if not Path(db_path).is_absolute():
            abs_db_path = PROJECT_ROOT / db_path
            settings.database_url = f"sqlite:///{abs_db_path}"

    settings.documents_path.mkdir(parents=True, exist_ok=True)
    settings.parent_store_path.parent.mkdir(parents=True, exist_ok=True)

    return settings


settings = get_settings()
