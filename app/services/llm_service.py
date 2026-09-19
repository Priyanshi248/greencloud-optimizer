from openai import AsyncOpenAI

from app.core.config import settings


class LLMService:
    """
    Handles text generation through OpenRouter.

    The LLM is responsible for language generation and explanation.
    Deterministic calculations remain outside this service.
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

        self.model = settings.LLM_MODEL

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generate a response using the configured LLM.
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            max_completion_tokens=1024,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "LLM returned an empty response"
            )

        return content