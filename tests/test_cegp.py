from app.algorithms.cegp import (
    CEGPAlgorithm,
    CandidateMetrics,
)


def test_cegp_selects_carbon_efficient_candidate():
    """
    Verify that CEGP can select the candidate with the
    best combined carbon/energy/cost score.
    """

    candidates = [
        CandidateMetrics(
            provider_id="provider-a",
            energy_kwh=4.0,
            carbon_kg=2.0,
            cost=1.0,
            execution_time_minutes=30,
        ),
        CandidateMetrics(
            provider_id="provider-b",
            energy_kwh=3.0,
            carbon_kg=1.0,
            cost=1.2,
            execution_time_minutes=30,
        ),
        CandidateMetrics(
            provider_id="provider-c",
            energy_kwh=5.0,
            carbon_kg=3.0,
            cost=0.8,
            execution_time_minutes=30,
        ),
    ]

    algorithm = CEGPAlgorithm()

    result = algorithm.optimize(
        candidates=candidates,
        deadline_minutes=60,
    )

    assert result.provider_id == "provider-b"


def test_cegp_rejects_deadline_violations():
    """
    Verify that candidates exceeding the deadline are removed
    before scoring.
    """

    candidates = [
        CandidateMetrics(
            provider_id="slow-provider",
            energy_kwh=1.0,
            carbon_kg=0.5,
            cost=0.5,
            execution_time_minutes=90,
        ),
        CandidateMetrics(
            provider_id="fast-provider",
            energy_kwh=2.0,
            carbon_kg=1.0,
            cost=1.0,
            execution_time_minutes=30,
        ),
    ]

    algorithm = CEGPAlgorithm()

    result = algorithm.optimize(
        candidates=candidates,
        deadline_minutes=60,
    )

    assert result.provider_id == "fast-provider"


def test_cegp_fails_when_no_candidate_meets_deadline():
    """
    Verify that optimization fails clearly when every candidate
    violates the deadline.
    """

    candidates = [
        CandidateMetrics(
            provider_id="provider-a",
            energy_kwh=1.0,
            carbon_kg=0.5,
            cost=0.5,
            execution_time_minutes=90,
        ),
    ]

    algorithm = CEGPAlgorithm()

    try:
        algorithm.optimize(
            candidates=candidates,
            deadline_minutes=60,
        )
        assert False, "Expected ValueError"
    except ValueError:
        assert True