from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserRole
from app.services.project_risk_service import (
    run_project_risk_assessment,
)


def scheduled_project_risk_scan() -> None:
    db: Session = SessionLocal()

    try:
        active_projects = (
            db.query(Project)
            .filter(
                Project.status == ProjectStatus.ACTIVE
            )
            .all()
        )

        # The automated scan needs an authorized government
        # identity because the existing risk service intentionally
        # protects the assessment endpoint.
        system_user = (
            db.query(User)
            .filter(
                User.role == UserRole.SUPER_ADMIN,
                User.is_active.is_(True),
            )
            .first()
        )

        if not system_user:
            return

        for project in active_projects:
            try:
                run_project_risk_assessment(
                    db=db,
                    project_id=project.id,
                    current_user=system_user,
                )
            except Exception:
                db.rollback()
                continue

    finally:
        db.close()