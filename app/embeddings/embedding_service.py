from openai import AsyncOpenAI

from app.core.config import settings


class EmbeddingService:
    """
    Generates embeddings through OpenRouter.

    OpenRouter exposes an OpenAI-compatible API, so we can use
    the OpenAI Python client while keeping the provider configurable.
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

        self.model = settings.EMBEDDING_MODEL

    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding vector for a single text chunk.
        """

        if not text.strip():
            raise ValueError("Text cannot be empty")

        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding