from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import (
    Connection,
)
from sqlalchemy.engine import (
    create_engine,
)

from youcode_ai.core.config import settings
from youcode_ai.infrastructure.database.base import (
    Base,
)
from youcode_ai.infrastructure.database.connection import (
    prepare_database_url,
)

# Importe toutes les tables pour les
# enregistrer dans Base.metadata.
from youcode_ai.infrastructure.database import (
    tables as _tables,
)


config = context.config

if config.config_file_name is not None:
    fileConfig(
        config.config_file_name
    )


database_url = prepare_database_url(
    settings.database_url
)

config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(
        hide_password=False
    ).replace("%", "%%"),
)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        compare_server_default=True,
        render_as_batch=(
            url.startswith("sqlite")
        ),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        configure_context(
            connection
        )

        with context.begin_transaction():
            context.run_migrations()


def configure_context(
    connection: Connection,
) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=(
            connection.dialect.name
            == "sqlite"
        ),
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()