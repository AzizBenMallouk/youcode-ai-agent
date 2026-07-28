"""AsyncPostgresSaver factory for LangGraph checkpointing.

Creates a PostgreSQL-backed checkpointer that persists conversation
state (LangGraph thread checkpoints) across service restarts.
"""

from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


@asynccontextmanager
async def create_checkpointer(postgres_uri: str):
    """Create and initialize a PostgreSQL checkpointer.

    Automatically creates the required LangGraph tables
    (checkpoints, checkpoint_writes) if they do not exist.

    Parameters
    ----------
    postgres_uri:
        Full PostgreSQL URI, e.g.
        ``postgresql+asyncpg://user:pass@host:5432/db``
        The ``+asyncpg`` driver suffix is stripped automatically.
    """
    clean_uri = postgres_uri.replace("+asyncpg", "")
    async with AsyncPostgresSaver.from_conn_string(clean_uri) as checkpointer:
        await checkpointer.setup()
        yield checkpointer
