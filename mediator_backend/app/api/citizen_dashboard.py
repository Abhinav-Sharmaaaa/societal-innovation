from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.citizen_dashboard import (
    CitizenDashboardResponse,
)
from app.services.citizen_dashboard_service import (
    get_citizen_dashboard,
)


router = APIRouter(
    prefix="/citizen-dashboard",
    tags=["Citizen Dashboard"],
)


@router.get(
    "",
    response_model=CitizenDashboardResponse,
)
def citizen_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.CITIZEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only citizens can access "
                "the citizen dashboard."
            ),
        )

    return get_citizen_dashboard(
        db=db,
        current_user=current_user,
    )