import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.greencloud_agent import GreenCloudAgent
from app.db.database import AsyncSessionLocal


async def run_test(
    db: AsyncSession,
    title: str,
    query: str,
    workload_id: UUID | None = None,
):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    agent = GreenCloudAgent(db)

    answer = await agent.answer(
        query=query,
        workload_id=workload_id,
    )

    print("\nAgent response:")
    print(answer)


async def main():

    # ---------------------------------------------------------
    # Get your seeded workload UUID
    # ---------------------------------------------------------

    workload_id = UUID(
        "fdba722a-d373-4019-850a-0f722207af24"
    )

    async with AsyncSessionLocal() as db:

        # -----------------------------------------------------
        # Test 1 — Knowledge question
        # -----------------------------------------------------

        await run_test(
            db=db,
            title="TEST 1 — LLM SELECTS RAG TOOL",
            query=(
                "What is the Carbon Efficient Green Policy "
                "and how does it reduce carbon emissions?"
            ),
        )

        # -----------------------------------------------------
        # Test 2 — Optimization question
        # -----------------------------------------------------

        await run_test(
            db=db,
            title="TEST 2 — LLM SELECTS OPTIMIZATION TOOL",
            query=(
                "Optimize this workload using the carbon-efficient "
                "strategy and tell me the resulting provider, "
                "energy consumption, carbon emissions, cost, "
                "and execution time."
            ),
            workload_id=workload_id,
        )


if __name__ == "__main__":
    asyncio.run(main())