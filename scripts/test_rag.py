import asyncio

from app.services.rag_service import RAGService


async def main():
    service = RAGService()

    question = (
        "What is the Carbon Efficient Green Policy "
        "and how does it help reduce carbon emissions?"
    )

    answer = await service.answer(
        query=question,
        limit=5,
    )

    print("\nRAG Answer:")
    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
    