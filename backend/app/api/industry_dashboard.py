from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.industry_dashboard import (
    IndustryDashboardResponse,
)
from app.services.industry_dashboard_service import (
    get_industry_dashboard,
)


router = APIRouter(
    prefix="/industry-dashboard",
    tags=["Industry Dashboard"],
)


@router.get(
    "",
    response_model=IndustryDashboardResponse,
)
def industry_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only industry users can access "
                "the industry dashboard."
            ),
        )

    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Industry user is not associated "
                "with an organization."
            ),
        )

    return get_industry_dashboard(
        db=db,
        current_user=current_user,
    )