from app.rag.retriever import RAGRetriever
from app.services.llm_service import LLMService


class RAGService:
    """
    Combines semantic document retrieval with LLM generation.

    The retriever finds relevant knowledge from the research
    knowledge base, while the LLM converts that context into
    a natural-language answer.
    """

    def __init__(self):
        self.retriever = RAGRetriever()
        self.llm_service = LLMService()

    async def answer(self, query: str, limit: int = 5) -> str:
        """
        Retrieve relevant research chunks and generate
        a grounded answer using the LLM.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")

        documents = await self.retriever.retrieve(
            query=query,
            limit=limit,
        )

        if not documents:
            return (
                "I could not find relevant information in the "
                "GreenCloud knowledge base."
            )

        context_parts = []

        for document in documents:
            context_parts.append(
                f"Source: {document.source_name}\n"
                f"Chunk: {document.chunk_index}\n"
                f"Content:\n{document.content}"
            )

        context = "\n\n---\n\n".join(context_parts)

        system_prompt = """
You are the knowledge assistant for GreenCloud Optimizer.

Answer the user's question using the provided research context.

Rules:
1. Ground your answer in the retrieved context.
2. Do not invent facts that are not supported by the context.
3. If the context does not contain enough information, say so.
4. Do not perform carbon, energy, cost, or optimization calculations.
5. Keep the answer clear and technically accurate.
"""

        user_prompt = f"""
Research Context:

{context}

---

User Question:

{query}
"""

        return await self.llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )