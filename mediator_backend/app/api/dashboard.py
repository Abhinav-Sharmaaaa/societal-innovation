from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.dashboard import (
    GovernmentDashboardResponse,
)
from app.services.dashboard_service import (
    get_government_dashboard,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/government",
    response_model=GovernmentDashboardResponse,
)
def government_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.SUPER_ADMIN,
        UserRole.REVIEW_OFFICER,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to access "
                "the government dashboard."
            ),
        )

    return get_government_dashboard(db)