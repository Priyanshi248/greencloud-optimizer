from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request model for the GreenCloud AI assistant.

    The workload_id is optional because some questions
    only require RAG-based knowledge retrieval.
    """

    message: str = Field(
        ...,
        min_length=1,
        description="User's natural-language question or request.",
    )

    workload_id: UUID | None = Field(
        default=None,
        description=(
            "Optional workload ID. Required when the user wants "
            "a specific workload to be optimized."
        ),
    )


class ChatResponse(BaseModel):
    """
    Response returned by the GreenCloud AI assistant.
    """

    answer: str