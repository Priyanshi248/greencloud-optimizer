from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.cloud_provider import CloudProvider
from app.models.workload import Workload
from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    ProviderCandidateResponse,
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
    # 4. Fetch selected provider
    # ---------------------------------------------------------

    provider_result = await db.execute(
        select(CloudProvider).where(
            CloudProvider.id == optimization_result.provider_id
        )
    )

    provider = provider_result.scalar_one_or_none()

    if provider is None:
        raise HTTPException(
            status_code=500,
            detail="Selected provider not found",
        )

    # ---------------------------------------------------------
    # 5. Return API-friendly response
    # ---------------------------------------------------------

    return OptimizationResponse(
        id=optimization_result.id,
        workload_id=optimization_result.workload_id,
        provider_id=optimization_result.provider_id,
        provider_name=provider.provider_name,
        region=provider.region,
        algorithm=optimization_result.algorithm,
        energy_consumption_kwh=optimization_result.energy_consumption_kwh,
        carbon_emissions_kg=optimization_result.carbon_emissions_kg,
        estimated_cost=optimization_result.estimated_cost,
        execution_time_minutes=optimization_result.execution_time_minutes,
        carbon_score=optimization_result.carbon_score,
    )


@router.get(
    "/candidates/{workload_id}",
    response_model=List[ProviderCandidateResponse],
)
async def get_candidates(
    workload_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate every active cloud provider for a workload.

    This endpoint does not select a provider.
    It calculates the metrics for each provider so the
    frontend can display a transparent comparison.
    """

    # ---------------------------------------------------------
    # 1. Find the workload
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 2. Calculate metrics for every provider
    # ---------------------------------------------------------

    service = OptimizationService(db)

    try:
        candidates = await service.get_candidate_metrics(
            workload
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # ---------------------------------------------------------
    # 3. Return provider comparison
    # ---------------------------------------------------------

    return candidates