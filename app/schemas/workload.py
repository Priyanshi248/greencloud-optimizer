from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums.workload import WorkloadType


class WorkloadCreate(BaseModel):
    """
    Data required to create a new cloud workload.

    The frontend sends these values when the user
    configures a workload.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    workload_type: WorkloadType

    cpu_cores: float = Field(
        gt=0,
    )

    memory_gb: float = Field(
        gt=0,
    )

    storage_gb: float = Field(
        gt=0,
    )

    runtime_minutes: float = Field(
        gt=0,
    )

    deadline_minutes: float = Field(
        gt=0,
    )

    data_transfer_gb: float = Field(
        ge=0,
    )


class WorkloadResponse(BaseModel):
    """
    Response returned after a workload is stored
    in PostgreSQL.
    """

    id: UUID

    name: str

    workload_type: WorkloadType

    cpu_cores: float

    memory_gb: float

    storage_gb: float

    runtime_minutes: float

    deadline_minutes: float

    data_transfer_gb: float

    model_config = ConfigDict(
        from_attributes=True
    )