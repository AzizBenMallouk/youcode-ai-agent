from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.connection import (
    engine,
)
from youcode_ai.infrastructure.database import (
    tables,
)


def initialize_database() -> None:
    # Les imports des tables seront ajoutés ici.
    # Ils permettent à SQLAlchemy de les
    # enregistrer dans Base.metadata.

    Base.metadata.create_all(
        bind=engine
    )