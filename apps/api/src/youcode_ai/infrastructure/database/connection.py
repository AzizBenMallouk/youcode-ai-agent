from collections.abc import (
    Generator,
    Iterator,
)
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import (
    Engine,
    create_engine,
)
from sqlalchemy.engine import (
    URL,
    make_url,
)
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)

from youcode_ai.core.config import (
    PROJECT_ROOT,
    settings,
)
from sqlite3 import (
    Connection as SQLiteConnection,
)
from sqlalchemy import event


def prepare_database_url(
    database_url: str,
) -> URL:
    url = make_url(database_url)

    if (
        url.drivername == "sqlite"
        and url.database
        and url.database != ":memory:"
    ):
        database_path = Path(
            url.database
        )

        if not database_path.is_absolute():
            database_path = (
                PROJECT_ROOT
                / database_path
            )

        database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        url = url.set(
            database=str(
                database_path.resolve()
            )
        )

    return url


def create_database_engine() -> Engine:
    database_url = prepare_database_url(
        settings.database_url
    )

    connect_args: dict = {}

    if database_url.drivername == "sqlite":
        connect_args[
            "check_same_thread"
        ] = False

    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        echo=(
            settings.app_debug
            and settings.app_env
            == "development"
        ),
    )


engine = create_database_engine()


SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

@event.listens_for(
    engine,
    "connect",
)

def enable_sqlite_foreign_keys(
    database_api_connection,
    connection_record,
) -> None:
    if isinstance(
        database_api_connection,
        SQLiteConnection,
    ):
        cursor = (
            database_api_connection
            .cursor()
        )

        cursor.execute(
            "PRAGMA foreign_keys=ON"
        )

        cursor.close()


def get_database_session(
) -> Generator[Session, None, None]:
    """
    Dépendance FastAPI.

    La route contrôle la transaction :
    commit ou rollback.
    """

    with SessionFactory() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


@contextmanager
def database_session(
) -> Iterator[Session]:
    """
    Utilisé en dehors de FastAPI :
    scripts, agents et workers.
    """

    with SessionFactory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()