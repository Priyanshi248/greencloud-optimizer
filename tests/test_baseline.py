from app.algorithms.baseline import (
    BaselineCandidate,
    ESTBaseline,
)


def test_est_selects_fastest_candidate():
    candidates = [
        BaselineCandidate(
            provider_id="provider-a",
            energy_kwh=3.0,
            carbon_kg=1.0,
            cost=1.0,
            execution_time_minutes=30,
        ),
        BaselineCandidate(
            provider_id="provider-b",
            energy_kwh=2.0,
            carbon_kg=0.5,
            cost=0.8,
            execution_time_minutes=45,
        ),
        BaselineCandidate(
            provider_id="provider-c",
            energy_kwh=4.0,
            carbon_kg=2.0,
            cost=1.2,
            execution_time_minutes=20,
        ),
    ]

    algorithm = ESTBaseline()

    result = algorithm.optimize(
        candidates=candidates,
        deadline_minutes=60,
    )

    assert result.provider_id == "provider-c"


def test_est_removes_deadline_violation():
    candidates = [
        BaselineCandidate(
            provider_id="fast-but-invalid",
            energy_kwh=1.0,
            carbon_kg=0.5,
            cost=0.5,
            execution_time_minutes=70,
        ),
        BaselineCandidate(
            provider_id="valid-provider",
            energy_kwh=2.0,
            carbon_kg=1.0,
            cost=1.0,
            execution_time_minutes=50,
        ),
    ]

    algorithm = ESTBaseline()

    result = algorithm.optimize(
        candidates=candidates,
        deadline_minutes=60,
    )

    assert result.provider_id == "valid-provider"