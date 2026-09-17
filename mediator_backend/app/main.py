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

from app.db.database import Base, engine
from app import models  # Import all models so they register with Base.metadata

@app.on_event("startup")
def run_migrations():
    print("Running database setup...")
    import os
    if os.path.exists("./mediator.db"):
        print("Removing old mediator.db to ensure clean schema...")
        os.remove("./mediator.db")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("Database setup complete.")
    except Exception as e:
        print(f"Failed to setup database: {e}")


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

from app.api.media import router as media_router
from app.api.rewards import router as rewards_router
app.include_router(media_router, prefix=settings.API_V1_PREFIX)
app.include_router(rewards_router, prefix=settings.API_V1_PREFIX)

@app.get("/", tags=["System"])
async def root():
    return {"message": "Mediator Backend Running", "status": "ok"}