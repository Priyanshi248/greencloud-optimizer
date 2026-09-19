from app.services.carbon_service import CarbonService


def test_carbon_emissions_calculation():
    """
    Verify the deterministic CO2 emissions calculation.
    """

    energy_kwh = 2.5

    # Example carbon intensity:
    # 0.4 kg CO2 per kWh
    carbon_intensity = 0.4

    emissions = CarbonService.calculate_emissions(
        energy_kwh,
        carbon_intensity,
    )

    # 2.5 × 0.4 = 1.0 kg CO2
    assert emissions == 1.0