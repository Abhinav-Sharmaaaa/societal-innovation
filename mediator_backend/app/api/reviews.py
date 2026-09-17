from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.challenge import ChallengeResponse
from app.schemas.review import (
    ReviewDecisionResponse,
    ReviewOverrideRequest,
)
from app.services.review_service import (
    accept_recommendation,
    get_review_history,
    get_review_queue,
    override_authority,
)


router = APIRouter(
    prefix="/reviews",
    tags=["Human Review"],
)


# ============================================================
# Review Queue
# ============================================================

@router.get(
    "/queue",
    response_model=list[ChallengeResponse],
)
async def review_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_review_queue(
        db=db,
        reviewer=current_user,
    )


# ============================================================
# Accept Recommendation
# ============================================================

@router.post(
    "/{challenge_id}/accept",
    response_model=ChallengeResponse,
)
async def accept_ai_recommendation(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return accept_recommendation(
        db=db,
        challenge_id=challenge_id,
        reviewer=current_user,
    )


# ============================================================
# Override Recommendation
# ============================================================

@router.post(
    "/{challenge_id}/override",
    response_model=ChallengeResponse,
)
async def override_ai_recommendation(
    challenge_id: int,
    payload: ReviewOverrideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return override_authority(
        db=db,
        challenge_id=challenge_id,
        reviewer=current_user,
        authority_id=payload.authority_id,
        reason=payload.reason,
    )


# ============================================================
# Review History
# ============================================================

@router.get(
    "/{challenge_id}/history",
    response_model=list[ReviewDecisionResponse],
)
async def review_history(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_review_history(
        db=db,
        challenge_id=challenge_id,
        reviewer=current_user,
    )