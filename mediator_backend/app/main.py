from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings

# ============================================================
# API ROUTERS
# ============================================================

from app.api.auth import router as auth_router
from app.api.challenges import router as challenges_router, util_router as challenges_util_router
from app.api.sync import router as sync_router

# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME + " Mediator",
    version=settings.APP_VERSION,
    description="Lightweight mediator for civic reports.",
)

import subprocess

@app.on_event("startup")
def run_migrations():
    print("Running database migrations...")
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migrations complete.")
    except Exception as e:
        print(f"Failed to run migrations: {e}")


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
app.include_router(sync_router, prefix="/api/v1")

@app.get("/", tags=["System"])
async def root():
    return {"message": "Mediator Backend Running", "status": "ok"}