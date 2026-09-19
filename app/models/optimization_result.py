import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OptimizationResult(Base):
    """
    Stores the result produced by the GreenCloud optimization engine.

    A result represents the selected cloud provider/region for a
    workload along with the estimated cost, energy consumption,
    carbon emissions, and scheduling information.
    """

    __tablename__ = "optimization_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    workload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workloads.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cloud_providers.id", ondelete="CASCADE"),
        nullable=False,
    )

    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    energy_consumption_kwh: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    carbon_emissions_kg: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    estimated_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    execution_time_minutes: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    carbon_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Link the optimization result to the workload that was optimized.
    workload = relationship(
        "Workload",
        back_populates="optimization_results",
    )

    # Link the optimization result to the selected cloud provider.
    provider = relationship(
        "CloudProvider",
        back_populates="optimization_results",
    )