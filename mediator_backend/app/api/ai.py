from fastapi import APIRouter, Depends

from app.ai.schemas import TriageRequest, TriageResponse
from app.ai.triage_service import triage_challenge
from app.ai.duplicate_service import find_duplicates
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.challenge_service import (
    get_challenge_by_id,
    persist_ai_triage_result,
)
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ============================================================
# Duplicate Check Schemas
# ============================================================

class DuplicateCheckRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1)
    category: str | None = None
    district: str | None = None
    state: str | None = None


class DuplicateMatch(BaseModel):
    id: int
    title: str
    description: str
    category: str | None
    status: str
    district: str | None
    state: str | None
    similarity_score: float


class DuplicateCheckResponse(BaseModel):
    has_duplicates: bool
    matches: list[DuplicateMatch]


@router.post(
    "/triage",
    response_model=TriageResponse,
)
def run_triage(
    request: TriageRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Run AI triage.

    When challenge_id is supplied, the authenticated submitter must
    own the challenge. The AI result is then persisted to PostgreSQL.
    Without challenge_id, this remains a non-persistent analysis call.
    """

    result = triage_challenge(request)

    challenge_id = getattr(request, "challenge_id", None)

    if challenge_id is not None:
        challenge = get_challenge_by_id(
            db,
            challenge_id,
        )

        if challenge is None:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=404,
                detail="Challenge not found.",
            )

        if challenge.submitted_by != current_user.id:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=403,
                detail="You are not authorized to analyze this challenge.",
            )

        persist_ai_triage_result(
            db,
            challenge,
            result,
        )

    return result


# ============================================================
# Duplicate Check
# ============================================================

@router.post(
    "/duplicate-check",
    response_model=DuplicateCheckResponse,
)
def check_duplicates(
    request: DuplicateCheckRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Check for potential duplicate challenges based on
    location (district / state) and issue similarity.

    Returns up to 5 ranked matches with similarity scores.
    """

    matches = find_duplicates(
        db,
        title=request.title,
        description=request.description,
        category=request.category,
        district=request.district,
        state=request.state,
    )

    return DuplicateCheckResponse(
        has_duplicates=len(matches) > 0,
        matches=[DuplicateMatch(**m) for m in matches],
    )
