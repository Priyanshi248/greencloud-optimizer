import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.workload import WorkloadType


class Workload(Base):
    """
    Represents a computational workload submitted to the
    GreenCloud Optimizer.

    The optimizer uses these resource requirements and timing
    constraints when deciding where the workload should execute.
    """

    __tablename__ = "workloads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    workload_type: Mapped[WorkloadType] = mapped_column(
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

    runtime_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    deadline_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    data_transfer_gb: Mapped[float] = mapped_column(
        Float,
        default=0.0,
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
    
    # One workload can have multiple optimization results,
    # for example results produced by CEGP and the baseline algorithm.
    optimization_results = relationship(
        "OptimizationResult",
        back_populates="workload",
        cascade="all, delete-orphan",
    )

