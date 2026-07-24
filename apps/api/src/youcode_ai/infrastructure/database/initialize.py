from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.connection import (
    engine,
)


def initialize_database() -> None:
    # On force l'import de toutes les tables
    # pour qu'Alembic ou Base.metadata.create_all
    # les découvre correctement.
    import youcode_ai.infrastructure.database.tables  # noqa: F401
    from youcode_ai.infrastructure.database.events import register_events

    Base.metadata.create_all(bind=engine)
    register_events()
