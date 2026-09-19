import asyncio

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.workload import Workload
from app.services.optimization_service import OptimizationService


async def main():
    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(Workload).limit(1)
        )

        workload = result.scalar_one()

        service = OptimizationService(db)

        # ---------------------------------------------------------
        # 1. Run CEGP
        # ---------------------------------------------------------

        cegp_result = await service.optimize(
            workload=workload,
            algorithm="cegp",
        )

        # ---------------------------------------------------------
        # 2. Run EST baseline
        # ---------------------------------------------------------

        est_result = await service.optimize(
            workload=workload,
            algorithm="est",
        )

        # ---------------------------------------------------------
        # 3. Display comparison
        # ---------------------------------------------------------

        print("\n" + "=" * 60)
        print("GREEN CLOUD OPTIMIZER — ALGORITHM COMPARISON")
        print("=" * 60)

        print(f"\nWorkload: {workload.name}")
        print(f"Deadline: {workload.deadline_minutes} minutes")

        print("\n--- CEGP ---")
        print(f"Provider ID : {cegp_result.provider_id}")
        print(f"Energy      : {cegp_result.energy_consumption_kwh:.4f} kWh")
        print(f"CO2         : {cegp_result.carbon_emissions_kg:.4f} kg")
        print(f"Cost        : ${cegp_result.estimated_cost:.4f}")
        print(f"Score       : {cegp_result.carbon_score:.4f}")

        print("\n--- EST BASELINE ---")
        print(f"Provider ID : {est_result.provider_id}")
        print(f"Energy      : {est_result.energy_consumption_kwh:.4f} kWh")
        print(f"CO2         : {est_result.carbon_emissions_kg:.4f} kg")
        print(f"Cost        : ${est_result.estimated_cost:.4f}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())