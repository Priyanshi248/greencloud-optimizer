import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.provider import CloudProviderType


class CloudProvider(Base):
    """
    Represents a cloud provider region/data center that can execute
    computational workloads.

    The optimizer evaluates these resources against workload
    requirements and environmental constraints.
    """

    __tablename__ = "cloud_providers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    provider_type: Mapped[CloudProviderType] = mapped_column(
        nullable=False,
    )

    provider_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    region: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    cpu_cores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    memory_gb: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    storage_gb: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    cpu_power_efficiency: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    dcie: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    execution_time_factor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    cost_per_cpu_hour: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # One cloud provider can have many carbon measurements.
    carbon_data = relationship(
        "CarbonData",
        back_populates="provider",
        cascade="all, delete-orphan",
    )

    # One cloud provider can have many optimization results.
    optimization_results = relationship(
        "OptimizationResult",
        back_populates="provider",
        cascade="all, delete-orphan",
    )