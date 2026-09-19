from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.optimization import router as optimization_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


# ---------------------------------------------------------
# API Routers
# ---------------------------------------------------------

app.include_router(optimization_router)
app.include_router(chat_router)


# ---------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "GreenCloud Optimizer API",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }