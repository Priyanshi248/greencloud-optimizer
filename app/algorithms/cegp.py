from dataclasses import dataclass


@dataclass
class CandidateMetrics:
    """
    Metrics calculated for one possible execution location.
    """

    provider_id: str
    energy_kwh: float
    carbon_kg: float
    cost: float
    execution_time_minutes: float


@dataclass
class CEGPResult:
    """
    Result returned by the CEGP algorithm.
    """

    provider_id: str
    score: float
    energy_kwh: float
    carbon_kg: float
    cost: float
    execution_time_minutes: float


class CEGPAlgorithm:
    """
    Carbon-aware scheduling algorithm.

    The algorithm:
    1. Removes candidates that cannot satisfy the deadline.
    2. Normalizes carbon, energy and cost.
    3. Calculates a weighted environmental/economic score.
    4. Selects the candidate with the lowest score.

    The algorithm does not access the database or LLM.
    """

    def __init__(
        self,
        carbon_weight: float = 0.6,
        energy_weight: float = 0.3,
        cost_weight: float = 0.1,
    ):
        self.carbon_weight = carbon_weight
        self.energy_weight = energy_weight
        self.cost_weight = cost_weight

    @staticmethod
    def _normalize(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """
        Min-max normalization.

        Returns 0 when all candidates have the same value.
        """

        if maximum == minimum:
            return 0.0

        return (value - minimum) / (maximum - minimum)

    def optimize(
        self,
        candidates: list[CandidateMetrics],
        deadline_minutes: float,
    ) -> CEGPResult:
        """
        Select the carbon-efficient candidate satisfying
        the workload deadline.
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

        carbon_values = [
            candidate.carbon_kg
            for candidate in feasible_candidates
        ]

        energy_values = [
            candidate.energy_kwh
            for candidate in feasible_candidates
        ]

        cost_values = [
            candidate.cost
            for candidate in feasible_candidates
        ]

        min_carbon = min(carbon_values)
        max_carbon = max(carbon_values)

        min_energy = min(energy_values)
        max_energy = max(energy_values)

        min_cost = min(cost_values)
        max_cost = max(cost_values)

        scored_candidates = []

        for candidate in feasible_candidates:
            normalized_carbon = self._normalize(
                candidate.carbon_kg,
                min_carbon,
                max_carbon,
            )

            normalized_energy = self._normalize(
                candidate.energy_kwh,
                min_energy,
                max_energy,
            )

            normalized_cost = self._normalize(
                candidate.cost,
                min_cost,
                max_cost,
            )

            score = (
                self.carbon_weight * normalized_carbon
                + self.energy_weight * normalized_energy
                + self.cost_weight * normalized_cost
            )

            scored_candidates.append(
                (
                    score,
                    candidate,
                )
            )

        best_score, best_candidate = min(
            scored_candidates,
            key=lambda item: item[0],
        )

        return CEGPResult(
            provider_id=best_candidate.provider_id,
            score=best_score,
            energy_kwh=best_candidate.energy_kwh,
            carbon_kg=best_candidate.carbon_kg,
            cost=best_candidate.cost,
            execution_time_minutes=best_candidate.execution_time_minutes,
        )