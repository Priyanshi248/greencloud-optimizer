from app.models.cloud_provider import CloudProvider
from app.models.workload import Workload


class EnergyService:
    """
    Calculates estimated energy consumption for a workload
    running on a cloud provider.

    This service contains deterministic energy calculations.
    It does not select the provider or perform optimization.
    """

    @staticmethod
    def calculate_energy(
        workload: Workload,
        provider: CloudProvider,
    ) -> float:
        """
        Estimate total energy consumption in kWh.

        The calculation considers:
        - CPU cores required by the workload
        - workload runtime
        - provider CPU power efficiency
        - provider data-center efficiency (DCiE)
        """

        runtime_hours = workload.runtime_minutes / 60

        cpu_energy = (
            workload.cpu_cores
            * runtime_hours
            * provider.cpu_power_efficiency
        )

        total_energy = cpu_energy / provider.dcie

        return total_energy