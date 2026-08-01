from shared.infrastructure.database.base import (
    Base,
)
from shared.infrastructure.database.connection import (
    engine,
)


def initialize_database() -> None:
    # On force l'import de toutes les tables
    # pour qu'Alembic ou Base.metadata.create_all
    # les découvre correctement.
    import shared.infrastructure.database.tables  # noqa: F401
    Base.metadata.create_all(bind=engine)
