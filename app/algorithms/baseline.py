from dataclasses import dataclass


@dataclass
class BaselineCandidate:
    """
    Candidate execution location evaluated by the EST baseline.
    """

    provider_id: str
    energy_kwh: float
    carbon_kg: float
    cost: float
    execution_time_minutes: float


@dataclass
class BaselineResult:
    """
    Result produced by the EST baseline.
    """

    provider_id: str
    energy_kwh: float
    carbon_kg: float
    cost: float
    execution_time_minutes: float


class ESTBaseline:
    """
    Earliest Start Time inspired baseline.

    For the prototype, execution time is used as the availability
    proxy. Among candidates capable of meeting the deadline, the
    candidate with the lowest execution time is selected.

    Carbon, energy and cost are deliberately not optimization
    objectives in this baseline.
    """

    def optimize(
        self,
        candidates: list[BaselineCandidate],
        deadline_minutes: float,
    ) -> BaselineResult:
        """
        Select the fastest feasible candidate.
        """

        feasible_candidates = [
            candidate
            for candidate in candidates
            if candidate.execution_time_minutes <= deadline_minutes
        ]

        if not feasible_candidates:
            raise ValueError(
                "No candidate can satisfy the workload deadline."
            )

        selected = min(
            feasible_candidates,
            key=lambda candidate: candidate.execution_time_minutes,
        )

        return BaselineResult(
            provider_id=selected.provider_id,
            energy_kwh=selected.energy_kwh,
            carbon_kg=selected.carbon_kg,
            cost=selected.cost,
            execution_time_minutes=selected.execution_time_minutes,
        )