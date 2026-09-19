from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OptimizationRequest(BaseModel):
    workload_id: UUID
    algorithm: str = "cegp"


class OptimizationResponse(BaseModel):
    id: UUID
    workload_id: UUID

    provider_id: UUID
    provider_name: str
    region: str

    algorithm: str

    energy_consumption_kwh: float
    carbon_emissions_kg: float
    estimated_cost: float
    execution_time_minutes: float
    carbon_score: float

    model_config = ConfigDict(from_attributes=True)

class ProviderCandidateResponse(BaseModel):
    provider_id: UUID
    provider_name: str
    provider_type: str
    region: str

    energy_kwh: float
    carbon_kg: float
    cost: float
    execution_time_minutes: float

    model_config = ConfigDict(from_attributes=True)