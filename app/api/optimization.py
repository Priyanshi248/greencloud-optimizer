from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.workload import Workload
from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
)
from app.services.optimization_service import OptimizationService


router = APIRouter(
    prefix="/optimization",
    tags=["Optimization"],
)


@router.post(
    "/run",
    response_model=OptimizationResponse,
)
async def run_optimization(
    request: OptimizationRequest,
    db: AsyncSession = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Find the requested workload
    # ---------------------------------------------------------

    result = await db.execute(
        select(Workload).where(
            Workload.id == request.workload_id
        )
    )

    workload = result.scalar_one_or_none()

    if workload is None:
        raise HTTPException(
            status_code=404,
            detail="Workload not found",
        )

    # ---------------------------------------------------------
    # 2. Validate the algorithm
    # ---------------------------------------------------------

    if request.algorithm not in {"cegp", "est"}:
        raise HTTPException(
            status_code=400,
            detail="Algorithm must be either 'cegp' or 'est'",
        )

    # ---------------------------------------------------------
    # 3. Run deterministic optimization
    # ---------------------------------------------------------

    service = OptimizationService(db)

    optimization_result = await service.optimize(
        workload=workload,
        algorithm=request.algorithm,
    )

    # ---------------------------------------------------------
    # 4. Return the persisted result
    # ---------------------------------------------------------

    return optimization_result