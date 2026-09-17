from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.university_dashboard import (
    UniversityDashboardResponse,
)
from app.services.university_dashboard_service import (
    get_university_dashboard,
)


router = APIRouter(
    prefix="/university-dashboard",
    tags=["University Dashboard"],
)


@router.get(
    "",
    response_model=UniversityDashboardResponse,
)
def university_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only university users can access "
                "the university dashboard."
            ),
        )

    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "University user is not associated "
                "with an organization."
            ),
        )

    return get_university_dashboard(
        db=db,
        current_user=current_user,
    )