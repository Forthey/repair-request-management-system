import asyncio
from logging.config import fileConfig


from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from config import settings

from database.database import Base

from database.models.address_orm import AddressORM
from database.models.application_orm import ApplicationORM
from database.models.client_orm import ClientORM
from database.models.contact_orm import ContactORM
from database.models.machine_orm import MachineORM
from database.models.worker_orm import WorkerORM
from database.models.other_orms import CompanyActivityORM, CloseReasonORM, ApplicationReasonORM, CompanyPositionORM


config = context.config

# TODO: change to Ubuntu later
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


config.set_main_option('sqlalchemy.url', settings.get_psycopg_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Добавлено для сравнения server_default
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
