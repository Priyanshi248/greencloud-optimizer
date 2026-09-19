from types import SimpleNamespace

from app.services.energy_service import EnergyService


def test_energy_calculation():
    """
    Verify the deterministic energy calculation.
    """

    workload = SimpleNamespace(
        cpu_cores=4,
        runtime_minutes=60,
    )

    provider = SimpleNamespace(
        cpu_power_efficiency=0.5,
        dcie=0.8,
    )

    energy = EnergyService.calculate_energy(
        workload,
        provider,
    )

    # 4 × 1 hour × 0.5 = 2 kWh CPU energy
    # 2 / 0.8 = 2.5 kWh total energy
    assert energy == 2.5