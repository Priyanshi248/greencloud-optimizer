from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.baseline import BaselineCandidate, ESTBaseline
from app.algorithms.cegp import CandidateMetrics, CEGPAlgorithm
from app.models.cloud_provider import CloudProvider
from app.models.optimization_result import OptimizationResult
from app.models.workload import Workload
from app.services.carbon_service import CarbonService
from app.services.cost_service import CostService
from app.services.energy_service import EnergyService


class OptimizationService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.carbon_service = CarbonService(db)

    async def optimize(
        self,
        workload: Workload,
        algorithm: str = "cegp",
    ):
        # ---------------------------------------------------------
        # 1. Get all active cloud providers
        # ---------------------------------------------------------

        result = await self.db.execute(
            select(CloudProvider).where(
                CloudProvider.is_active.is_(True)
            )
        )

        providers = result.scalars().all()

        if not providers:
            raise ValueError(
                "No active cloud providers are available."
            )

        # ---------------------------------------------------------
        # 2. Calculate metrics for every provider
        # ---------------------------------------------------------

        cegp_candidates = []
        est_candidates = []

        for provider in providers:

            carbon_intensity = (
                await self.carbon_service.get_latest_carbon_intensity(
                    provider.id
                )
            )

            energy_kwh = EnergyService.calculate_energy(
                workload,
                provider,
            )

            carbon_kg = CarbonService.calculate_emissions(
                energy_kwh,
                carbon_intensity,
            )

            cost = CostService.calculate_cost(
                workload,
                provider,
            )

            execution_time = (
                workload.runtime_minutes
                * provider.execution_time_factor
            )

            cegp_candidates.append(
                CandidateMetrics(
                    provider_id=str(provider.id),
                    energy_kwh=energy_kwh,
                    carbon_kg=carbon_kg,
                    cost=cost,
                    execution_time_minutes=execution_time,
                )
            )

            est_candidates.append(
                BaselineCandidate(
                    provider_id=str(provider.id),
                    energy_kwh=energy_kwh,
                    carbon_kg=carbon_kg,
                    cost=cost,
                    execution_time_minutes=execution_time,
                )
            )

        # ---------------------------------------------------------
        # 3. Run selected optimization algorithm
        # ---------------------------------------------------------

        if algorithm.lower() == "cegp":

            selected = CEGPAlgorithm().optimize(
                candidates=cegp_candidates,
                deadline_minutes=workload.deadline_minutes,
            )

            selected_algorithm = "CEGP"

        elif algorithm.lower() == "est":

            selected = ESTBaseline().optimize(
                candidates=est_candidates,
                deadline_minutes=workload.deadline_minutes,
            )

            selected_algorithm = "EST"

        else:
            raise ValueError(
                f"Unsupported optimization algorithm: {algorithm}"
            )

        # ---------------------------------------------------------
        # 4. Create optimization result
        # ---------------------------------------------------------

        provider_id = UUID(selected.provider_id)

        optimization_result = OptimizationResult(
            workload_id=workload.id,
            provider_id=provider_id,
            algorithm=selected_algorithm,
            energy_consumption_kwh=selected.energy_kwh,
            carbon_emissions_kg=selected.carbon_kg,
            estimated_cost=selected.cost,
            execution_time_minutes=selected.execution_time_minutes,
            carbon_score=getattr(selected, "score", 0.0),
        )

        self.db.add(optimization_result)

        await self.db.commit()
        await self.db.refresh(optimization_result)

        return optimization_result

    async def get_candidate_metrics(
        self,
        workload: Workload,
    ):
        """
        Calculate the metrics for every active cloud provider.

        This method does NOT select a provider.
        It only evaluates every provider so the frontend
        can display a transparent comparison.
        """

        # ---------------------------------------------------------
        # 1. Get all active providers
        # ---------------------------------------------------------

        result = await self.db.execute(
            select(CloudProvider).where(
                CloudProvider.is_active.is_(True)
            )
        )

        providers = result.scalars().all()

        if not providers:
            raise ValueError(
                "No active cloud providers are available."
            )

        candidates = []

        # ---------------------------------------------------------
        # 2. Calculate metrics for every provider
        # ---------------------------------------------------------

        for provider in providers:

            carbon_intensity = (
                await self.carbon_service.get_latest_carbon_intensity(
                    provider.id
                )
            )

            energy_kwh = EnergyService.calculate_energy(
                workload,
                provider,
            )

            carbon_kg = CarbonService.calculate_emissions(
                energy_kwh,
                carbon_intensity,
            )

            cost = CostService.calculate_cost(
                workload,
                provider,
            )

            execution_time = (
                workload.runtime_minutes
                * provider.execution_time_factor
            )

            candidates.append(
                {
                    "provider_id": str(provider.id),
                    "provider_name": provider.provider_name,
                    "provider_type": provider.provider_type.value,
                    "region": provider.region,
                    "energy_kwh": energy_kwh,
                    "carbon_kg": carbon_kg,
                    "cost": cost,
                    "execution_time_minutes": execution_time,
                }
            )

        # ---------------------------------------------------------
        # 3. Return all provider metrics
        # ---------------------------------------------------------

        return candidates