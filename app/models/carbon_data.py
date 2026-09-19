import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CarbonData(Base):
    """
    Represents carbon-intensity information associated with a
    cloud provider region.
    """

    __tablename__ = "carbon_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cloud_providers.id", ondelete="CASCADE"),
        nullable=False,
    )

    carbon_intensity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measurement_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Connect this carbon record back to its cloud provider.
    provider = relationship(
        "CloudProvider",
        back_populates="carbon_data",
    )