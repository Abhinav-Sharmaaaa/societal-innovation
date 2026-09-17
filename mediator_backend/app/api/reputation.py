from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.reputation import (
    ReputationEventResponse,
    ReputationScoreResponse,
)
from app.services.reputation_service import (
    get_organization_reputation,
    get_reputation_history,
    get_user_reputation,
)


router = APIRouter(
    prefix="/reputation",
    tags=["Reputation"],
)


@router.get(
    "/me",
    response_model=ReputationScoreResponse | None,
)
def get_my_reputation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.organization_id:
        return get_organization_reputation(
            db=db,
            organization_id=current_user.organization_id,
        )

    return get_user_reputation(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/history",
    response_model=list[ReputationEventResponse],
)
def get_my_reputation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.organization_id:
        return get_reputation_history(
            db=db,
            organization_id=current_user.organization_id,
        )

    return get_reputation_history(
        db=db,
        user_id=current_user.id,
    )