import asyncio

from app.services.llm_service import LLMService


async def main():
    service = LLMService()

    response = await service.generate(
        system_prompt=(
            "You are a helpful assistant for a cloud "
            "sustainability platform."
        ),
        user_prompt=(
            "Explain carbon-aware cloud computing in "
            "two sentences."
        ),
    )

    print("\nLLM Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())