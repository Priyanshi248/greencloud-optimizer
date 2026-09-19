from app.db.database import AsyncSessionLocal
from app.embeddings.embedding_service import EmbeddingService
from app.repositories.document_repository import DocumentRepository


class RAGRetriever:
    """
    Retrieves relevant knowledge from the vector database.

    The retriever is responsible only for:
    1. Embedding the user's query.
    2. Performing vector similarity search.
    3. Returning the most relevant document chunks.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
    ):
        """
        Retrieve the most relevant document chunks for a query.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        query_embedding = (
            await self.embedding_service.generate_embedding(
                query
            )
        )

        async with AsyncSessionLocal() as db:
            repository = DocumentRepository(db)

            documents = await repository.similarity_search(
                embedding=query_embedding,
                limit=limit,
            )

        return documents