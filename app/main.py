from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.optimization import router as optimization_router
from app.core.config import settings
from app.api.workloads import router as workloads_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)



# =========================================================
# CORS
# =========================================================
#
# Allows the local HTML/CSS/JavaScript frontend to communicate
# with the FastAPI backend during development.
#
# Later, when the frontend is deployed, we will replace/add
# the deployed frontend URL here.
#

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://greencloud-optimizer.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(workloads_router)
app.include_router(optimization_router)
app.include_router(chat_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():
    return {
        "message": "GreenCloud Optimizer API",
        "version": settings.APP_VERSION,
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }