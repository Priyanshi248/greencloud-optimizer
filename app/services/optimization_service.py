from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.baseline import (
    BaselineCandidate,
    ESTBaseline,
)
from app.algorithms.cegp import (
    CandidateMetrics,
    CEGPAlgorithm,
)
from app.models.cloud_provider import CloudProvider
from app.models.optimization_result import OptimizationResult
from app.models.workload import Workload
from app.services.carbon_service import CarbonService
from app.services.cost_service import CostService
from app.services.energy_service import EnergyService


class OptimizationService:
    """
    Orchestrates the GreenCloud optimization workflow.

    This service connects database entities, deterministic
    calculation services and optimization algorithms.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.carbon_service = CarbonService(db)

    async def optimize(
        self,
        workload: Workload,
        algorithm: str = "cegp",
    ) -> OptimizationResult:
        """
        Optimize a workload across all active cloud providers.

        Supported algorithms:
        - cegp
        - est
        """

        # ---------------------------------------------------------
        # 1. Retrieve active cloud providers
        # ---------------------------------------------------------

        result = await self.db.execute(
            select(CloudProvider)
            .where(CloudProvider.is_active.is_(True))
        )

        providers = result.scalars().all()

        if not providers:
            raise ValueError(
                "No active cloud providers are available."
            )

        # ---------------------------------------------------------
        # 2. Calculate metrics for every provider
        # ---------------------------------------------------------

        cegp_candidates: list[CandidateMetrics] = []
        est_candidates: list[BaselineCandidate] = []

        for provider in providers:

            # Get the latest available carbon intensity.
            carbon_intensity = (
                await self.carbon_service.get_latest_carbon_intensity(
                    provider.id
                )
            )

            # Calculate deterministic metrics.
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

            # -----------------------------------------------------
            # Candidate for CEGP
            # -----------------------------------------------------

            cegp_candidates.append(
                CandidateMetrics(
                    provider_id=str(provider.id),
                    energy_kwh=energy_kwh,
                    carbon_kg=carbon_kg,
                    cost=cost,
                    execution_time_minutes=(
                        workload.runtime_minutes * provider.execution_time_factor
                    ),
                )
            )

            # -----------------------------------------------------
            # Candidate for EST baseline
            # -----------------------------------------------------

            est_candidates.append(
                BaselineCandidate(
                    provider_id=str(provider.id),
                    energy_kwh=energy_kwh,
                    carbon_kg=carbon_kg,
                    cost=cost,
                    execution_time_minutes=(
                        workload.runtime_minutes * provider.execution_time_factor
                    ),
                )
            )

        # ---------------------------------------------------------
        # 3. Run selected optimization algorithm
        # ---------------------------------------------------------

        if algorithm.lower() == "cegp":

            optimizer = CEGPAlgorithm()

            selected = optimizer.optimize(
                candidates=cegp_candidates,
                deadline_minutes=workload.deadline_minutes,
            )

            selected_algorithm = "CEGP"

        elif algorithm.lower() == "est":

            optimizer = ESTBaseline()

            selected = optimizer.optimize(
                candidates=est_candidates,
                deadline_minutes=workload.deadline_minutes,
            )

            selected_algorithm = "EST"

        else:
            raise ValueError(
                f"Unsupported optimization algorithm: {algorithm}"
            )

        # ---------------------------------------------------------
        # 4. Convert provider ID back to UUID
        # ---------------------------------------------------------

        provider_id = UUID(selected.provider_id)

        # ---------------------------------------------------------
        # 5. Persist optimization result
        # ---------------------------------------------------------

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