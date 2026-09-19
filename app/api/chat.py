from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.greencloud_agent import GreenCloudAgent
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a natural-language request through the
    GreenCloud agent.

    The agent may use:
    - RAG knowledge retrieval
    - deterministic optimization tools
    """

    agent = GreenCloudAgent(db)

    answer = await agent.answer(
        query=request.message,
        workload_id=request.workload_id,
    )

    return ChatResponse(answer=answer)