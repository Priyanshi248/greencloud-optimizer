from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OptimizationRequest(BaseModel):
    workload_id: UUID
    algorithm: str = "cegp"


class OptimizationResponse(BaseModel):
    id: UUID
    workload_id: UUID
    provider_id: UUID
    algorithm: str
    energy_consumption_kwh: float
    carbon_emissions_kg: float
    estimated_cost: float
    execution_time_minutes: float
    carbon_score: float

    model_config = ConfigDict(from_attributes=True)