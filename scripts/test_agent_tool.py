import asyncio
from uuid import UUID

from app.db.database import AsyncSessionLocal
from app.agents.tools import run_optimization_tool


async def main():
    # Use the workload UUID from your seeded database.
    workload_id = UUID("fdba722a-d373-4019-850a-0f722207af24")

    async with AsyncSessionLocal() as db:
        result = await run_optimization_tool(
            db=db,
            workload_id=workload_id,
            algorithm="cegp",
        )

    print("\nOptimization Tool Result:")
    print("=" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())