from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.reputation_score import (
    ReputationScoreEntityType,
)
from app.models.user import User, UserRole
from app.services.analytics_service import (
    get_analytics_overview,
    get_district_analytics,
    get_industry_leaderboard,
    get_reputation_leaderboard,
    get_university_leaderboard,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def _require_analytics_access(
    current_user: User,
) -> None:

    if current_user.role not in {
        UserRole.SUPER_ADMIN,
        UserRole.REVIEW_OFFICER,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to "
                "access platform analytics."
            ),
        )


@router.get("/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_analytics_access(current_user)

    return get_analytics_overview(db)


@router.get("/districts")
def district_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_analytics_access(current_user)

    return get_district_analytics(db)


@router.get("/universities")
def university_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_analytics_access(current_user)

    return get_university_leaderboard(db)


@router.get("/industries")
def industry_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_analytics_access(current_user)

    return get_industry_leaderboard(db)


@router.get("/reputation")
def reputation_leaderboard(
    entity_type: ReputationScoreEntityType | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_analytics_access(current_user)

    return get_reputation_leaderboard(
        db=db,
        entity_type=entity_type,
    )