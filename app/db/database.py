from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


# Create the asynchronous database engine.
#
# The engine manages connections between our FastAPI application
# and PostgreSQL.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


# Factory used to create AsyncSession objects.
#
# Each request that needs database access can obtain a session
# from this factory.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Provide an asynchronous SQLAlchemy database session.

    FastAPI can use this function as a dependency in API routes.
    The session is automatically closed after the request finishes.
    """

    async with AsyncSessionLocal() as session:
        yield session