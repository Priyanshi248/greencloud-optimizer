from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.

    Every model in app/models will inherit from this class.
    Alembic will use this metadata to detect database schema changes.
    """

    pass