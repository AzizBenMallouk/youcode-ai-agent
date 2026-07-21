import os
from dataclasses import dataclass
from typing import (
    Literal,
    cast,
)

from dotenv import load_dotenv


load_dotenv()


ChatProvider = Literal[
    "gemini",
    "ollama",
]

EmbeddingProvider = Literal[
    "gemini",
    "ollama",
]


def get_required_env(
    name: str,
) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise ValueError(
            "Missing environment variable: "
            f"{name}"
        )

    return value.strip()


def get_optional_env(
    name: str,
) -> str | None:
    value = os.getenv(name)

    if value is None:
        return None

    normalized_value = value.strip()

    if not normalized_value:
        return None

    return normalized_value


def get_string_env(
    name: str,
    default: str,
) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    return value.strip()


def get_bool_env(
    name: str,
    default: bool = False,
) -> bool:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    normalized_value = (
        value.strip().lower()
    )

    if normalized_value in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True

    if normalized_value in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False

    raise ValueError(
        f"Invalid boolean value for {name}: "
        f"{value}"
    )


def get_int_env(
    name: str,
    default: int,
) -> int:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    try:
        return int(value)

    except ValueError as error:
        raise ValueError(
            f"Invalid integer value for "
            f"{name}: {value}"
        ) from error


def get_float_env(
    name: str,
    default: float,
) -> float:
    value = os.getenv(name)

    if value is None or not value.strip():
        return default

    try:
        return float(value)

    except ValueError as error:
        raise ValueError(
            f"Invalid float value for "
            f"{name}: {value}"
        ) from error


def get_provider_env(
    name: str,
    default: str,
) -> str:
    value = get_string_env(
        name=name,
        default=default,
    ).lower()

    allowed_providers = {
        "gemini",
        "ollama",
    }

    if value not in allowed_providers:
        raise ValueError(
            f"Invalid provider for {name}: "
            f"{value}. Expected one of: "
            f"{sorted(allowed_providers)}"
        )

    return value


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_debug: bool

    # Providers
    chat_provider: ChatProvider
    embedding_provider: EmbeddingProvider

    # Gemini
    google_api_key: str | None
    gemini_chat_model: str
    gemini_embedding_model: str

    # Ollama
    ollama_base_url: str
    ollama_chat_model: str
    ollama_embedding_model: str

    # Paramètres communs du modèle
    model_temperature: float

    # Qdrant
    qdrant_url: str
    qdrant_document_collection: str
    qdrant_knowledge_gap_collection: str

    # Knowledge gaps
    knowledge_gap_similarity_threshold: float
    knowledge_gap_minimum_coverage: float

    # RAG
    parent_store_path: str
    documents_path: str
    rag_top_k: int
    rag_score_threshold: float

    # Base SQL
    database_url: str

    # Mémoire conversationnelle
    max_history_messages: int

    # Consentement
    consent_version: str
    consent_token_ttl_minutes: int
    consent_secret_key: str

    # API externe des sessions
    test_session_api_url: str
    test_session_api_timeout: float
    test_session_api_key: str | None


def load_settings() -> Settings:
    chat_provider_value = get_provider_env(
        name="CHAT_PROVIDER",
        default="gemini",
    )

    embedding_provider_value = (
        get_provider_env(
            name="EMBEDDING_PROVIDER",
            default="gemini",
        )
    )

    chat_provider = cast(
        ChatProvider,
        chat_provider_value,
    )

    embedding_provider = cast(
        EmbeddingProvider,
        embedding_provider_value,
    )

    google_api_key = get_optional_env(
        "GOOGLE_API_KEY"
    )

    uses_gemini = (
        chat_provider == "gemini"
        or embedding_provider == "gemini"
    )

    if uses_gemini and not google_api_key:
        raise ValueError(
            "GOOGLE_API_KEY is required "
            "when Gemini is used as chat "
            "or embedding provider."
        )

    settings = Settings(
        app_name=get_string_env(
            name="APP_NAME",
            default="YouCode AI Guide",
        ),
        app_env=get_string_env(
            name="APP_ENV",
            default="development",
        ),
        app_debug=get_bool_env(
            name="APP_DEBUG",
            default=False,
        ),

        chat_provider=chat_provider,
        embedding_provider=(
            embedding_provider
        ),

        google_api_key=google_api_key,
        gemini_chat_model=get_string_env(
            name="GEMINI_CHAT_MODEL",
            default="gemini-2.5-flash",
        ),
        gemini_embedding_model=(
            get_string_env(
                name=(
                    "GEMINI_EMBEDDING_MODEL"
                ),
                default=(
                    "models/"
                    "gemini-embedding-001"
                ),
            )
        ),

        ollama_base_url=get_string_env(
            name="OLLAMA_BASE_URL",
            default=(
                "http://127.0.0.1:11434"
            ),
        ),
        ollama_chat_model=get_string_env(
            name="OLLAMA_CHAT_MODEL",
            default="llama3.2:3b",
        ),
        ollama_embedding_model=(
            get_string_env(
                name=(
                    "OLLAMA_EMBEDDING_MODEL"
                ),
                default="nomic-embed-text",
            )
        ),

        model_temperature=get_float_env(
            name="MODEL_TEMPERATURE",
            default=0.0,
        ),

        qdrant_url=get_string_env(
            name="QDRANT_URL",
            default=(
                "http://127.0.0.1:6333"
            ),
        ),
        qdrant_document_collection=(
            get_required_env(
                "QDRANT_DOCUMENT_COLLECTION"
            )
        ),
        qdrant_knowledge_gap_collection=(
            get_required_env(
                "QDRANT_KNOWLEDGE_GAP_COLLECTION"
            )
        ),

        knowledge_gap_similarity_threshold=(
            get_float_env(
                name=(
                    "KNOWLEDGE_GAP_"
                    "SIMILARITY_THRESHOLD"
                ),
                default=0.88,
            )
        ),
        knowledge_gap_minimum_coverage=(
            get_float_env(
                name=(
                    "KNOWLEDGE_GAP_"
                    "MINIMUM_COVERAGE"
                ),
                default=0.6,
            )
        ),

        parent_store_path=get_string_env(
            name="PARENT_STORE_PATH",
            default=(
                "data/parent_store.json"
            ),
        ),
        documents_path=get_string_env(
            name="DOCUMENTS_PATH",
            default="data/documents",
        ),
        rag_top_k=get_int_env(
            name="RAG_TOP_K",
            default=5,
        ),
        rag_score_threshold=get_float_env(
            name="RAG_SCORE_THRESHOLD",
            default=0.55,
        ),

        database_url=get_string_env(
            name="DATABASE_URL",
            default=(
                "sqlite:///data/youcode.db"
            ),
        ),

        max_history_messages=get_int_env(
            name="MAX_HISTORY_MESSAGES",
            default=12,
        ),

        consent_version=get_string_env(
            name="CONSENT_VERSION",
            default="v1",
        ),
        consent_token_ttl_minutes=(
            get_int_env(
                name=(
                    "CONSENT_TOKEN_TTL_MINUTES"
                ),
                default=30,
            )
        ),
        consent_secret_key=(
            get_required_env(
                "CONSENT_SECRET_KEY"
            )
        ),

        test_session_api_url=(
            get_string_env(
                name="TEST_SESSION_API_URL",
                default=(
                    "http://127.0.0.1:9003"
                ),
            )
        ),
        test_session_api_timeout=(
            get_float_env(
                name=(
                    "TEST_SESSION_API_TIMEOUT"
                ),
                default=10.0,
            )
        ),
        test_session_api_key=(
            get_optional_env(
                "TEST_SESSION_API_KEY"
            )
        ),
    )

    validate_settings(settings)

    return settings


def validate_settings(
    settings: Settings,
) -> None:
    if settings.rag_top_k < 1:
        raise ValueError(
            "RAG_TOP_K must be greater "
            "than or equal to 1."
        )

    if not (
        0
        <= settings.rag_score_threshold
        <= 1
    ):
        raise ValueError(
            "RAG_SCORE_THRESHOLD must "
            "be between 0 and 1."
        )

    if not (
        0
        <= settings
        .knowledge_gap_similarity_threshold
        <= 1
    ):
        raise ValueError(
            "KNOWLEDGE_GAP_SIMILARITY_"
            "THRESHOLD must be between "
            "0 and 1."
        )

    if not (
        0
        <= settings
        .knowledge_gap_minimum_coverage
        <= 1
    ):
        raise ValueError(
            "KNOWLEDGE_GAP_MINIMUM_COVERAGE "
            "must be between 0 and 1."
        )

    if settings.max_history_messages < 1:
        raise ValueError(
            "MAX_HISTORY_MESSAGES must "
            "be greater than or equal to 1."
        )

    if (
        settings
        .consent_token_ttl_minutes
        < 1
    ):
        raise ValueError(
            "CONSENT_TOKEN_TTL_MINUTES "
            "must be greater than or "
            "equal to 1."
        )

    if settings.test_session_api_timeout <= 0:
        raise ValueError(
            "TEST_SESSION_API_TIMEOUT "
            "must be greater than 0."
        )

    if not (
        0
        <= settings.model_temperature
        <= 2
    ):
        raise ValueError(
            "MODEL_TEMPERATURE must "
            "be between 0 and 2."
        )


settings = load_settings()