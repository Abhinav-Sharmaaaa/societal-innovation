from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.routing import AuthorityRoutingResponse
from app.services.authority_routing_service import (
    find_best_authority,
)
from app.services.challenge_service import (
    get_challenge_by_id,
)


router = APIRouter(
    prefix="/routing",
    tags=["Routing"],
)


@router.get(
    "/challenges/{challenge_id}/recommendation",
    response_model=AuthorityRoutingResponse,
)
async def get_authority_recommendation(
    challenge_id: int,
    db: Session = Depends(get_db),
):
    challenge = get_challenge_by_id(
        db=db,
        challenge_id=challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    result = find_best_authority(
        db=db,
        challenge=challenge,
    )

    return AuthorityRoutingResponse(
        recommended_authority_id=(
            result.recommended_authority_id
        ),
        recommended_authority_name=(
            result.recommended_authority_name
        ),
        score=result.score,
        reason=result.reason,
        candidates=result.candidates,
    )