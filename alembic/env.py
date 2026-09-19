from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.config import settings
from app.db.base import Base

# Import all models so SQLAlchemy registers their tables
# in Base.metadata.
from app.models import (
    CarbonData,
    CloudProvider,
    Document,
    OptimizationResult,
    Workload,
)


# Alembic configuration object.
config = context.config


# Normalize the database URL for SQLAlchemy + asyncpg.
#
# Neon provides a standard PostgreSQL URL:
#     postgresql://...
#
# Our application uses:
#     postgresql+asyncpg://...
#
# We convert it here so Alembic uses the same async driver
# as the application.
database_url = make_url(settings.DATABASE_URL)

if database_url.drivername in {"postgresql", "postgres"}:
    database_url = database_url.set(
        drivername="postgresql+asyncpg"
    )


# Neon commonly provides libpq-style parameters such as:
# sslmode=require
# channel_binding=require
#
# These are not passed directly to asyncpg.
# Convert/remove them before creating the async engine.
query = dict(database_url.query)

if "sslmode" in query:
    sslmode = query.pop("sslmode")

    if sslmode == "require":
        query["ssl"] = "require"

query.pop("channel_binding", None)

database_url = database_url.set(query=query)


# Use the normalized URL for Alembic.
config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(hide_password=False).replace("%", "%%"),
)


# Configure logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Alembic compares this metadata against the actual database schema.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
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


def do_run_migrations(connection) -> None:
    """
    Configure Alembic using an active database connection.
    """

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Create an asynchronous database engine and run migrations.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            do_run_migrations
        )

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations against the live PostgreSQL database.
    """

    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()