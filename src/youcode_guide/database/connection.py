from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from youcode_guide.config import settings


class Base(DeclarativeBase):
    pass


def prepare_sqlite_directory() -> None:
    prefix = "sqlite:///"

    if not settings.database_url.startswith(
        prefix
    ):
        return

    database_path = settings.database_url[
        len(prefix):
    ]

    Path(database_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )


prepare_sqlite_directory()


engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,
    },
)


SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def create_database_session() -> Session:
    return SessionFactory()