"""Fixtures de test partagées."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlite3 import Connection as SQLiteConnection

from youcode_ai.infrastructure.database.base import Base


@pytest.fixture(scope="session")
def test_engine():
    """Moteur SQLite en mémoire pour les tests."""

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
    )

    @event.listens_for(engine, "connect")
    def enable_fk(
        dbapi_conn, conn_record
    ):
        if isinstance(
            dbapi_conn, SQLiteConnection
        ):
            cursor = dbapi_conn.cursor()
            cursor.execute(
                "PRAGMA foreign_keys=ON"
            )
            cursor.close()

    # Import toutes les tables
    import youcode_ai.infrastructure.database.tables  # noqa: F401

    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Session de test avec rollback."""

    factory = sessionmaker(
        bind=test_engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )

    with factory() as session:
        yield session
        session.rollback()
