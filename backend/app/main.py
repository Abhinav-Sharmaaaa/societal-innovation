from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings

# ============================================================
# API ROUTERS
# ============================================================

from app.api.auth import router as auth_router
from app.api.challenges import router as challenges_router
from app.api.ai import router as ai_router
from app.api.organizations import router as organizations_router
from app.api.admin import router as admin_router
from app.api.location import router as location_router
from app.api.routing import router as routing_router
from app.api.reviews import router as reviews_router
from app.api.innovation_opportunities import (
    router as innovation_opportunities_router,
)
from app.api.rfps import router as rfps_router
from app.api.university_matching import (
    router as university_matching_router,
)
from app.api.rfp_invitations import (
    router as rfp_invitations_router,
)
from app.api.university_proposals import (
    router as university_proposals_router,
)
from app.api.proposal_evaluations import (
    router as proposal_evaluations_router,
)
from app.api.industry_collaboration import (
    router as industry_collaboration_router,
)
from app.api.projects import router as projects_router
from app.api.project_milestones import (
    router as project_milestones_router,
)
from app.api.project_deliverables import (
    router as project_deliverables_router,
)
from app.api.project_funding import (
    router as project_funding_router,
)
from app.api.project_reports import (
    router as project_reports_router,
)
from app.api.project_outcomes import (
    router as project_outcomes_router,
)
from app.api.project_risks import (
    router as project_risks_router,
)
from app.api.notifications import (
    router as notifications_router,
)
from app.api.reputation import (
    router as reputation_router,
)
from app.api.media import (
    router as media_router,
)
from app.api.rewards import (
    router as rewards_router,
)

# Dashboard routers
from app.api.dashboard import (
    router as dashboard_router,
)
from app.api.university_dashboard import (
    router as university_dashboard_router,
)
from app.api.industry_dashboard import (
    router as industry_dashboard_router,
)
from app.api.citizen_dashboard import (
    router as citizen_dashboard_router,
)
from app.api.action_center import (
    router as action_center_router,
)

# ============================================================
# SCHEDULER SERVICES
# ============================================================

from app.services.project_risk_scheduler import (
    scheduled_project_risk_scan,
)
from app.services.deadline_scheduler import (
    scheduled_deadline_scan,
)


#Analytics routers
from app.api.analytics import (
    router as analytics_router,
)

# ============================================================
# APPLICATION
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


# ============================================================
# SCHEDULER
# ============================================================

scheduler = BackgroundScheduler()


# ============================================================
# STATIC FILES
# ============================================================

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
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

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

app.include_router(
    organizations_router,
    prefix="/api/v1",
)

app.include_router(
    admin_router,
    prefix="/api/v1",
)

app.include_router(
    location_router,
    prefix="/api/v1",
)

app.include_router(
    routing_router,
    prefix="/api/v1",
)

app.include_router(
    reviews_router,
    prefix="/api/v1",
)

app.include_router(
    innovation_opportunities_router,
    prefix="/api/v1",
)

app.include_router(
    rfps_router,
    prefix="/api/v1",
)

app.include_router(
    university_matching_router,
    prefix="/api/v1",
)

app.include_router(
    rfp_invitations_router,
    prefix="/api/v1",
)

app.include_router(
    university_proposals_router,
    prefix="/api/v1",
)

app.include_router(
    proposal_evaluations_router,
    prefix="/api/v1",
)

app.include_router(
    industry_collaboration_router,
    prefix="/api/v1",
)

app.include_router(
    projects_router,
    prefix="/api/v1",
)

app.include_router(
    project_milestones_router,
    prefix="/api/v1",
)

app.include_router(
    project_deliverables_router,
    prefix="/api/v1",
)

app.include_router(
    project_funding_router,
    prefix="/api/v1",
)

app.include_router(
    project_reports_router,
    prefix="/api/v1",
)

app.include_router(
    project_outcomes_router,
    prefix="/api/v1",
)

app.include_router(
    project_risks_router,
    prefix="/api/v1",
)

app.include_router(
    notifications_router,
    prefix="/api/v1",
)

app.include_router(
    reputation_router,
    prefix="/api/v1",
)

app.include_router(
    analytics_router,
    prefix="/api/v1",
)

app.include_router(
    media_router,
    prefix="/api/v1",
)

app.include_router(
    rewards_router,
    prefix="/api/v1",
)

# ============================================================
# DASHBOARD ROUTERS
# ============================================================

app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    university_dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    industry_dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    citizen_dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    action_center_router,
    prefix="/api/v1",
)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
async def root():
    return {
        "message": settings.APP_NAME,
        "status": "running",
        "version": settings.APP_VERSION,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/api/v1/health",
    tags=["System"],
)
async def health_check():
    return {
        "status": "ok",
        "service": "backend",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# ============================================================
# SCHEDULER STARTUP
# ============================================================

@app.on_event("startup")
def start_scheduler():

    # --------------------------------------------------------
    # Project Risk Scan
    # --------------------------------------------------------
    scheduler.add_job(
        scheduled_project_risk_scan,
        trigger="interval",
        hours=1,
        id="project-risk-scan",
        replace_existing=True,
    )

    # --------------------------------------------------------
    # Deadline Scan
    # --------------------------------------------------------
    scheduler.add_job(
        scheduled_deadline_scan,
        trigger="interval",
        hours=1,
        id="deadline-scan",
        replace_existing=True,
    )



    # --------------------------------------------------------
    # Start APScheduler
    # --------------------------------------------------------
    if not scheduler.running:
        scheduler.start()


# ============================================================
# SCHEDULER SHUTDOWN
# ============================================================

@app.on_event("shutdown")
def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown(wait=False)