from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.workload import Workload
from app.schemas.workload import (
    WorkloadCreate,
    WorkloadResponse,
)


router = APIRouter(
    prefix="/workloads",
    tags=["Workloads"],
)


@router.post(
    "",
    response_model=WorkloadResponse,
    status_code=201,
)
async def create_workload(
    workload_data: WorkloadCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new workload in PostgreSQL.

    The frontend sends the workload configuration here.
    The optimization engine later uses the returned
    workload ID to evaluate cloud providers.
    """

    workload = Workload(
        name=workload_data.name,
        workload_type=workload_data.workload_type,
        cpu_cores=workload_data.cpu_cores,
        memory_gb=workload_data.memory_gb,
        storage_gb=workload_data.storage_gb,
        runtime_minutes=workload_data.runtime_minutes,
        deadline_minutes=workload_data.deadline_minutes,
        data_transfer_gb=workload_data.data_transfer_gb,
    )

    db.add(workload)

    await db.commit()

    await db.refresh(workload)

    return workload


@router.get(
    "/{workload_id}",
    response_model=WorkloadResponse,
)
async def get_workload(
    workload_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a workload by its UUID.

    This is useful for inspecting the workload that was
    used for an optimization run.
    """

    result = await db.execute(
        select(Workload).where(
            Workload.id == workload_id
        )
    )

    workload = result.scalar_one_or_none()

    if workload is None:
        raise HTTPException(
            status_code=404,
            detail="Workload not found",
        )

    return workload