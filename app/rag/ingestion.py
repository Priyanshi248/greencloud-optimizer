from pathlib import Path

from pypdf import PdfReader

from app.db.database import AsyncSessionLocal
from app.embeddings.embedding_service import EmbeddingService
from app.rag.chunker import DocumentChunker
from app.repositories.document_repository import DocumentRepository


class DocumentIngestionService:
    """
    Converts PDF documents into searchable vector chunks.

    Responsibilities:
    1. Extract text from a PDF.
    2. Split the text into chunks.
    3. Generate embeddings for each chunk.
    4. Store the chunks and embeddings in PostgreSQL.
    """

    def __init__(self):
        self.chunker = DocumentChunker(
            chunk_size=1000,
            chunk_overlap=200,
        )

        self.embedding_service = EmbeddingService()

    @staticmethod
    def extract_text(pdf_path: str | Path) -> str:
        """
        Extract text from all pages of a PDF.
        """

        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {path}"
            )

        reader = PdfReader(path)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        document_text = "\n\n".join(pages).strip()

        if not document_text:
            raise ValueError(
                f"No extractable text found in PDF: {path}"
            )

        return document_text

    async def ingest_pdf(
        self,
        pdf_path: str | Path,
    ) -> int:
        """
        Ingest a PDF into the vector knowledge base.

        Returns the number of chunks stored.
        """

        path = Path(pdf_path)

        text = self.extract_text(path)

        chunks = self.chunker.chunk(text)

        if not chunks:
            return 0

        async with AsyncSessionLocal() as db:
            repository = DocumentRepository(db)
            if await repository.source_exists(path.name):
                return 0

            for chunk in chunks:
                embedding = (
                    await self.embedding_service.generate_embedding(
                        chunk.content
                    )
                )

                await repository.create(
                    source_name=path.name,
                    source_type="pdf",
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    embedding=embedding,
                )

            await db.commit()

        return len(chunks)