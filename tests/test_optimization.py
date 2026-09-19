from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.optimization_service import OptimizationService


@pytest.mark.asyncio
async def test_optimization_service_runs_cegp():
    """
    Verify that OptimizationService:
    - retrieves active providers
    - calculates energy
    - calculates carbon emissions
    - calculates cost
    - executes the real CEGP algorithm
    - creates an OptimizationResult
    """

    workload_id = uuid4()
    provider_1_id = uuid4()
    provider_2_id = uuid4()

    workload = SimpleNamespace(
        id=workload_id,
        cpu_cores=4,
        runtime_minutes=60,
        deadline_minutes=120,
    )

    provider_1 = SimpleNamespace(
        id=provider_1_id,
        is_active=True,
        cpu_power_efficiency=0.5,
        dcie=0.8,
        cost_per_cpu_hour=0.30,
        execution_time_factor=1.0,
    )

    provider_2 = SimpleNamespace(
        id=provider_2_id,
        is_active=True,
        cpu_power_efficiency=0.4,
        dcie=0.9,
        cost_per_cpu_hour=0.20,
        execution_time_factor=0.9,
    )

    class FakeScalarResult:
        def all(self):
            return [provider_1, provider_2]

    class FakeExecuteResult:
        def scalars(self):
            return FakeScalarResult()

    class FakeDB:
        def __init__(self):
            self.added = None

        async def execute(self, statement):
            return FakeExecuteResult()

        def add(self, obj):
            self.added = obj

        async def commit(self):
            pass

        async def refresh(self, obj):
            pass

    fake_db = FakeDB()

    service = OptimizationService(fake_db)

    # ---------------------------------------------------------
    # Mock only the external carbon-data lookup.
    # The actual energy, cost, carbon calculation and CEGP
    # algorithm remain real.
    # ---------------------------------------------------------

    async def fake_carbon_intensity(provider_id):
        if provider_id == provider_1_id:
            return 0.30

        return 0.10

    service.carbon_service.get_latest_carbon_intensity = (
        fake_carbon_intensity
    )

    result = await service.optimize(
        workload=workload,
        algorithm="cegp",
    )

    # ---------------------------------------------------------
    # Verify the optimization result
    # ---------------------------------------------------------

    assert result.algorithm == "CEGP"

    assert result.workload_id == workload_id

    assert result.provider_id == provider_2_id

    assert result.energy_consumption_kwh > 0

    assert result.carbon_emissions_kg > 0

    assert result.estimated_cost > 0

    assert result.execution_time_minutes == 54.0

    # The service should have persisted an OptimizationResult.
    assert fake_db.added is result