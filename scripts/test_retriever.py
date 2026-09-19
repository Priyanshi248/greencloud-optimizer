import asyncio

from app.rag.retriever import RAGRetriever


async def main():
    retriever = RAGRetriever()

    query = (
        "How does carbon-aware scheduling reduce "
        "carbon emissions in cloud computing?"
    )

    documents = await retriever.retrieve(
        query=query,
        limit=5,
    )

    print(f"\nRetrieved {len(documents)} chunks\n")

    for document in documents:
        print("=" * 70)
        print(f"Source: {document.source_name}")
        print(f"Chunk: {document.chunk_index}")
        print(document.content[:500])
        print()


if __name__ == "__main__":
    asyncio.run(main())