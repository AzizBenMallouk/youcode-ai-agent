from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
from youcode_ai.infrastructure.database.connection import (
    database_session,
)


def get_database_session() -> Generator[
    Session,
    None,
    None,
]:
    with database_session() as session:
        yield session


DatabaseSession = Annotated[
    Session,
    Depends(get_database_session),
]
