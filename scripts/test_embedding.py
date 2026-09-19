import asyncio

from app.embeddings.embedding_service import EmbeddingService


async def main():
    service = EmbeddingService()

    embedding = await service.generate_embedding(
        "Carbon-aware cloud scheduling"
    )

    print("Embedding dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])


if __name__ == "__main__":
    asyncio.run(main())