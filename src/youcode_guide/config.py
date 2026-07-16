import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise ValueError(
            f"Missing environment variable: {name}"
        )

    return value.strip()


def get_bool_env(
    name: str,
    default: bool = False,
) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_int_env(
    name: str,
    default: int,
) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    return int(value)


def get_float_env(
    name: str,
    default: float,
) -> float:
    value = os.getenv(name)

    if value is None:
        return default

    return float(value)


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_debug: bool

    google_api_key: str
    gemini_chat_model: str
    gemini_embedding_model: str

    qdrant_url: str
    qdrant_collection: str
    parent_store_path: str

    database_url: str
    documents_path: str

    rag_top_k: int
    rag_score_threshold: float

    max_history_messages: int

    consent_version: str
    consent_token_ttl_minutes: int
    consent_secret_key: str

def load_settings() -> Settings:
    return Settings(
        app_name=get_required_env("APP_NAME"),
        app_env=get_required_env("APP_ENV"),
        app_debug=get_bool_env(
            "APP_DEBUG",
            default=False,
        ),
        google_api_key=get_required_env(
            "GOOGLE_API_KEY"
        ),
        gemini_chat_model=get_required_env(
            "GEMINI_CHAT_MODEL"
        ),
        gemini_embedding_model=get_required_env(
            "GEMINI_EMBEDDING_MODEL"
        ),
        qdrant_url=get_required_env(
            "QDRANT_URL"
        ),
        qdrant_collection=get_required_env(
            "QDRANT_COLLECTION"
        ),
        parent_store_path=get_required_env(
            "PARENT_STORE_PATH"
        ),
        database_url=get_required_env(
            "DATABASE_URL"
        ),
        documents_path=get_required_env(
            "DOCUMENTS_PATH"
        ),
        rag_top_k=get_int_env(
            "RAG_TOP_K",
            default=5,
        ),
        rag_score_threshold=get_float_env(
            "RAG_SCORE_THRESHOLD",
            default=0.55,
        ),
        max_history_messages=get_int_env(
            "MAX_HISTORY_MESSAGES",
            default=12,
        ),
        consent_version=get_required_env(
            "CONSENT_VERSION"
        ),
        consent_token_ttl_minutes=get_int_env(
            "CONSENT_TOKEN_TTL_MINUTES",
            default=30,
        ),
        consent_secret_key=get_required_env(
            "CONSENT_SECRET_KEY"
        ),
    )


settings = load_settings()