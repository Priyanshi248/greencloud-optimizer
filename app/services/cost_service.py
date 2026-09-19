from app.models.cloud_provider import CloudProvider
from app.models.workload import Workload


class CostService:
    """
    Calculates the estimated execution cost of a workload
    on a cloud provider.

    This service contains deterministic cost calculations.
    It does not make optimization decisions.
    """

    @staticmethod
    def calculate_cost(
        workload: Workload,
        provider: CloudProvider,
    ) -> float:
        """
        Estimate workload execution cost.

        Cost is calculated using:
        CPU cores × runtime in hours × provider's
        cost per CPU hour.
        """

        runtime_hours = workload.runtime_minutes / 60

        estimated_cost = (
            workload.cpu_cores
            * runtime_hours
            * provider.cost_per_cpu_hour
        )

        return estimated_cost