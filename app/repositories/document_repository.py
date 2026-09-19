from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    """
    Handles persistence and semantic retrieval of RAG documents.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        source_name: str,
        source_type: str,
        chunk_index: int,
        content: str,
        embedding: list[float],
    ) -> Document:
        """
        Store a document chunk and its embedding.
        """

        document = Document(
            source_name=source_name,
            source_type=source_type,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
        )

        self.db.add(document)

        await self.db.flush()

        return document

    async def similarity_search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[Document]:
        """
        Retrieve the most semantically similar document chunks
        using pgvector cosine distance.
        """

        statement = (
            select(Document)
            .order_by(
                Document.embedding.cosine_distance(embedding)
            )
            .limit(limit)
        )

        result = await self.db.execute(statement)

        return list(result.scalars().all())

    async def get_by_id(
        self,
        document_id: UUID,
    ) -> Document | None:
        """
        Retrieve a single stored document chunk by ID.
        """

        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        return result.scalar_one_or_none()

    async def source_exists(
        self,
        source_name: str,
    ) -> bool:
        """
        Check whether a source has already been ingested.
        """

        result = await self.db.execute(
            select(Document.id)
            .where(Document.source_name == source_name)
            .limit(1)
        )

        return result.scalar_one_or_none() is not None