import asyncio
import sys

from app.rag.ingestion import DocumentIngestionService


async def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m scripts.ingest_document "
            "<path-to-pdf>"
        )
        return

    pdf_path = sys.argv[1]

    print(f"\nIngesting: {pdf_path}")

    service = DocumentIngestionService()

    chunk_count = await service.ingest_pdf(pdf_path)

    if chunk_count == 0:
        print(
            "No new chunks were inserted. "
            "The document may already exist."
        )
        return

    print(
        f"Successfully ingested document "
        f"into {chunk_count} chunks."
    )


if __name__ == "__main__":
    asyncio.run(main())