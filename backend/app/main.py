from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router

from app.api.challenges import router as challenges_router
from app.api.ai import router as ai_router

from fastapi.staticfiles import StaticFiles
# ============================================================
# Application
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered platform for collecting societal challenges, "
        "intelligently routing them, matching universities and "
        "industry partners, and tracking solution projects."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#API Routers

app.include_router(
    auth_router,
    prefix=settings.API_V1_PREFIX,
) 

app.include_router(
    challenges_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    ai_router,
    prefix=settings.API_V1_PREFIX,
)

# ============================================================
# Root
# ============================================================

@app.get("/", tags=["System"])
async def root():
    return {
        "message": settings.APP_NAME,
        "status": "running",
        "version": settings.APP_VERSION,
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/api/v1/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "service": "backend",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }