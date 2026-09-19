from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cloud_provider import CloudProvider
from app.models.workload import Workload
from app.services.optimization_service import OptimizationService


async def run_optimization_tool(
    db: AsyncSession,
    workload_id: UUID,
    algorithm: str = "cegp",
) -> dict:
    """
    Agent-facing tool for running GreenCloud optimization.

    The agent supplies a workload ID and algorithm.
    The tool retrieves the workload and delegates the actual
    optimization to the deterministic OptimizationService.

    The selected provider's human-readable information is also
    returned so that the AI does not need to infer it from a UUID.
    """

    # ---------------------------------------------------------
    # 1. Retrieve the requested workload
    # ---------------------------------------------------------

    result = await db.execute(
        select(Workload).where(Workload.id == workload_id)
    )

    workload = result.scalar_one_or_none()

    if workload is None:
        raise ValueError(
            f"Workload not found: {workload_id}"
        )

    # ---------------------------------------------------------
    # 2. Delegate optimization to the deterministic service
    # ---------------------------------------------------------

    service = OptimizationService(db)

    optimization_result = await service.optimize(
        workload=workload,
        algorithm=algorithm,
    )

    # ---------------------------------------------------------
    # 3. Retrieve selected provider details
    # ---------------------------------------------------------

    provider_result = await db.execute(
        select(CloudProvider).where(
            CloudProvider.id == optimization_result.provider_id
        )
    )

    provider = provider_result.scalar_one_or_none()

    if provider is None:
        raise ValueError(
            f"Selected provider not found: "
            f"{optimization_result.provider_id}"
        )

    # ---------------------------------------------------------
    # 4. Return a JSON-friendly result to the agent
    # ---------------------------------------------------------

    return {
        "optimization_result_id": str(
            optimization_result.id
        ),
        "workload_id": str(
            optimization_result.workload_id
        ),

        # Provider information
        "provider_id": str(
            optimization_result.provider_id
        ),
        "provider_name": provider.provider_name,
        "provider_type": provider.provider_type.value,
        "region": provider.region,

        # Optimization information
        "algorithm": optimization_result.algorithm,

        # Deterministic metrics
        "energy_consumption_kwh": (
            optimization_result.energy_consumption_kwh
        ),
        "carbon_emissions_kg": (
            optimization_result.carbon_emissions_kg
        ),
        "estimated_cost": (
            optimization_result.estimated_cost
        ),
        "execution_time_minutes": (
            optimization_result.execution_time_minutes
        ),
        "carbon_score": (
            optimization_result.carbon_score
        ),
    }


# =============================================================
# OpenRouter tool schemas
# =============================================================

OPTIMIZATION_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "optimize_workload",
        "description": (
            "Run the deterministic GreenCloud optimization engine "
            "for a workload. Use this when the user asks to optimize "
            "a workload, select a cloud provider, or determine "
            "carbon-efficient execution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "workload_id": {
                    "type": "string",
                    "description": (
                        "UUID of the workload to optimize. "
                        "If the application already provides a "
                        "workload ID, that ID is authoritative."
                    ),
                },
                "algorithm": {
                    "type": "string",
                    "enum": ["cegp", "est"],
                    "description": (
                        "Optimization algorithm. Use CEGP for "
                        "carbon-efficient optimization or EST for "
                        "the execution-time baseline."
                    ),
                },
            },
            "required": [],
        },
    },
}


RAG_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_greencloud_knowledge",
        "description": (
            "Search the GreenCloud research knowledge base using "
            "semantic retrieval. Use this for questions about "
            "CEGP, carbon-aware scheduling, Green Broker, carbon "
            "emissions, cloud sustainability, or concepts described "
            "in the research documents."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Question or information to search for."
                    ),
                },
            },
            "required": ["query"],
        },
    },
}


AGENT_TOOLS = [
    RAG_TOOL_SCHEMA,
    OPTIMIZATION_TOOL_SCHEMA,
]