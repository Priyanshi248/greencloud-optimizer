from types import SimpleNamespace

from app.services.cost_service import CostService


def test_cost_calculation():
    """
    Verify the deterministic cost calculation.
    """

    workload = SimpleNamespace(
        cpu_cores=4,
        runtime_minutes=60,
    )

    provider = SimpleNamespace(
        cost_per_cpu_hour=0.25,
    )

    cost = CostService.calculate_cost(
        workload,
        provider,
    )

    # 4 CPU cores × 1 hour × $0.25 = $1.00
    assert cost == 1.0