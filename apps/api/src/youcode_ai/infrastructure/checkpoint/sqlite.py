import sqlite3
from functools import lru_cache
from pathlib import Path

from langgraph.checkpoint.sqlite import (
    SqliteSaver,
)

from youcode_ai.core.config import (
    settings,
)


@lru_cache(maxsize=1)
def create_sqlite_checkpointer(
) -> SqliteSaver:
    """
    Crée un checkpointer SQLite persistant.

    La connexion reste ouverte pendant toute la
    durée de vie de l'application.
    """

    database_path = Path(
        settings.langgraph_checkpoint_path
    )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(database_path),
        check_same_thread=False,
    )

    connection.execute(
        "PRAGMA journal_mode=WAL"
    )

    connection.execute(
        "PRAGMA busy_timeout=5000"
    )

    checkpointer = SqliteSaver(
        connection
    )

    checkpointer.setup()

    return checkpointer