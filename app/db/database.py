from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


# Neon provides a standard PostgreSQL URL:
# postgresql://...
#
# SQLAlchemy's async engine requires:
# postgresql+asyncpg://...
#
# We therefore normalize the URL here instead of modifying
# the connection string supplied by Neon.
database_url = make_url(settings.DATABASE_URL)

# If the URL does not already specify a driver, use asyncpg.
if database_url.drivername in {"postgresql", "postgres"}:
    database_url = database_url.set(drivername="postgresql+asyncpg")

# Neon commonly provides libpq-style parameters such as:
# sslmode=require
# channel_binding=require
#
# These are not valid asyncpg connection keyword arguments,
# so remove them from the URL.
query = dict(database_url.query)
query.pop("sslmode", None)
query.pop("channel_binding", None)

database_url = database_url.set(query=query)

# Neon requires SSL.
# Local PostgreSQL does not.
connect_args = {}

if database_url.host and "neon.tech" in database_url.host:
    connect_args["ssl"] = True


engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session