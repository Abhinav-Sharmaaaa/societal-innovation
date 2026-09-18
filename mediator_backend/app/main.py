from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings

# ============================================================
# API ROUTERS
# ============================================================

from app.api.auth import router as auth_router
from app.api.challenges import router as challenges_router, util_router as challenges_util_router

# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME + " Mediator",
    version=settings.APP_VERSION,
    description="Lightweight mediator for civic reports.",
)

from app.db.database import Base, engine
from app import models  # Import all models so they register with Base.metadata


# ============================================================
# STATIC FILES
# ============================================================

import os
os.makedirs("uploads", exist_ok=True)
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# API ROUTERS
# ============================================================

app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(challenges_router, prefix=settings.API_V1_PREFIX)
app.include_router(challenges_util_router, prefix=settings.API_V1_PREFIX)

from app.api.media import router as media_router
from app.api.rewards import router as rewards_router
app.include_router(media_router, prefix=settings.API_V1_PREFIX)
app.include_router(rewards_router, prefix=settings.API_V1_PREFIX)

@app.get("/", tags=["System"])
async def root():
    return {"message": "Mediator Backend Running", "status": "ok"}