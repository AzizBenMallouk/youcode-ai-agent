import logging

from sqlalchemy import event
from youcode_ai.infrastructure.database.base import Base
from youcode_ai.infrastructure.database.mcp_client import mcp_sheets_client

logger = logging.getLogger(__name__)

TARGET_TABLES = {
    "newsletter_subscriptions",
    "newsletter_preferences",
    "email_deliveries",
    "knowledge_gaps",
    "knowledge_gap_questions",
    "visitor_requests",
    "consent_grants",
}


def sync_to_google_sheets(mapper, connection, target):
    """
    Synchronise l'entité avec Google Sheets via MCP.
    Note : Google Sheets agit ici comme un journal d'audit append-only pour simplifier
    la migration des données sans impacter les performances de lecture.
    """
    table_name = target.__tablename__
    if table_name in TARGET_TABLES:
        try:
            row_data = {}
            for column in target.__table__.columns:
                val = getattr(target, column.name)
                if val is not None:
                    row_data[column.name] = str(val)

            # Action synchrone car les hooks SQLAlchemy le sont
            mcp_sheets_client.sync_append_row(table_name, row_data)
        except Exception as e:
            logger.error(f"Failed to sync {table_name} to Google Sheets via MCP: {e}")


def register_events():
    """Enregistre les hooks SQLAlchemy."""
    for model_class in Base.__subclasses__():
        if (
            hasattr(model_class, "__tablename__")
            and model_class.__tablename__ in TARGET_TABLES
        ):
            event.listen(model_class, "after_insert", sync_to_google_sheets)
            # Optionnel: on peut aussi écouter after_update si on veut logguer les modifications
            event.listen(model_class, "after_update", sync_to_google_sheets)
