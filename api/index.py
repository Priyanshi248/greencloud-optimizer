from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.optimization import router as optimization_router
from app.api.workloads import router as workloads_router


app = FastAPI(
    title="GreenCloud Optimizer",
    version="1.0.0",
)


app.include_router(
    workloads_router,
    prefix="/api",
)

app.include_router(
    optimization_router,
    prefix="/api",
)

app.include_router(
    chat_router,
    prefix="/api",
)


@app.get("/api")
async def root():
    return {
        "message": "GreenCloud Optimizer API",
        "version": "1.0.0",
    }


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
    }