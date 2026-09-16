from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.challenge_evidence import ChallengeEvidence
from app.models.user import User
from app.schemas.assignment import (
    ChallengeAssignmentCreate,
    ChallengeAssignmentResponse,
    ChallengeEscalateRequest,
    ChallengeReassignRequest,
)
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeResponse,
    ChallengeUpdate,
)
from app.schemas.evidence import EvidenceResponse
from app.services.challenge_assignment_service import (
    assign_challenge,
    auto_route_challenge,
    escalate_challenge,
    get_assignment_history,
    get_transfer_authorities,
    reassign_challenge,
)
from app.services.challenge_service import (
    create_challenge,
    get_challenge_by_id,
    get_challenges,
    get_user_challenges,
    update_challenge,
)
from app.services.file_service import save_upload


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"],
)


# ============================================================
# Create Challenge
# ============================================================


@router.post(
    "",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_challenge(
    challenge_data: ChallengeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit a new societal challenge.

    Any authenticated user can submit a challenge for now.
    Later we can apply finer-grained submission policies.
    """

    return create_challenge(
        db=db,
        challenge_data=challenge_data,
        current_user=current_user,
    )


# ============================================================
# List Challenges
# ============================================================


@router.get(
    "",
    response_model=list[ChallengeResponse],
)
async def list_challenges(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve challenges with pagination.
    """

    return get_challenges(
        db=db,
        skip=skip,
        limit=limit,
    )


# ============================================================
# Get My Challenges
# ============================================================


@router.get(
    "/my",
    response_model=list[ChallengeResponse],
)
async def list_my_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve challenges submitted by the authenticated user.
    """

    return get_user_challenges(
        db=db,
        user_id=current_user.id,
    )


# ============================================================
# Get Challenge By ID
# ============================================================


@router.get(
    "/{challenge_id}",
    response_model=ChallengeResponse,
)
async def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single challenge.
    """

    challenge = get_challenge_by_id(
        db=db,
        challenge_id=challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    return challenge


# ============================================================
# Update Challenge
# ============================================================


@router.patch(
    "/{challenge_id}",
    response_model=ChallengeResponse,
)
async def update_existing_challenge(
    challenge_id: int,
    challenge_data: ChallengeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a challenge.

    Only the original submitter can modify it at this stage.
    """

    challenge = get_challenge_by_id(
        db=db,
        challenge_id=challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    if challenge.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only update your own challenges."
            ),
        )

    return update_challenge(
        db=db,
        challenge=challenge,
        challenge_data=challenge_data,
    )


# ============================================================
# Upload Challenge Evidence
# ============================================================


@router.post(
    "/{challenge_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_challenge_evidence(
    challenge_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload an image, video, or PDF document for a challenge.

    Only the original challenge submitter can upload evidence
    at this stage.
    """

    # --------------------------------------------------------
    # Find challenge
    # --------------------------------------------------------

    challenge = get_challenge_by_id(
        db=db,
        challenge_id=challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if challenge.submitted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only upload evidence to your own "
                "challenges."
            ),
        )

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    try:
        file_metadata = await save_upload(file)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    evidence = ChallengeEvidence(
        challenge_id=challenge.id,
        evidence_type=file_metadata[
            "evidence_type"
        ],
        original_filename=file_metadata[
            "original_filename"
        ],
        stored_filename=file_metadata[
            "stored_filename"
        ],
        content_type=file_metadata[
            "content_type"
        ],
        file_size=file_metadata[
            "file_size"
        ],
        file_url=file_metadata[
            "file_url"
        ],
        uploaded_by=current_user.id,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


# ============================================================
# Challenge Assignment
# ============================================================


@router.post(
    "/{challenge_id}/assign",
    response_model=ChallengeResponse,
)
async def assign_challenge_to_authority(
    challenge_id: int,
    payload: ChallengeAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign a challenge to an authorized authority organization.

    This is only valid when the challenge has no current
    authority.
    """

    return assign_challenge(
        db=db,
        challenge_id=challenge_id,
        authority_id=payload.authority_id,
        performed_by=current_user,
        remarks=payload.remarks,
    )


# ============================================================
# Automatic Routing
# ============================================================


@router.post(
    "/{challenge_id}/auto-route",
    response_model=ChallengeResponse,
)
async def automatically_route_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate the best authority using the routing engine and
    automatically assign the challenge when policy permits.

    Automatic routing is only allowed for:
    - authorized official users
    - challenges whose AI analysis does not require review
    - strong authority matches
    """

    return auto_route_challenge(
        db=db,
        challenge_id=challenge_id,
        performed_by=current_user,
    )


# ============================================================
# Dynamic Transfer Authorities
# ============================================================


@router.get(
    "/{challenge_id}/transfer-authorities",
)
async def get_challenge_transfer_authorities(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return active destination authorities for the current
    challenge.

    The result is calculated dynamically from the database.
    The current authority itself is excluded.
    """

    return get_transfer_authorities(
        db=db,
        challenge_id=challenge_id,
        performed_by=current_user,
    )


# ============================================================
# Assignment History
# ============================================================


@router.get(
    "/{challenge_id}/assignment-history",
    response_model=list[ChallengeAssignmentResponse],
)
async def get_challenge_assignment_history(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the complete authority assignment history.
    """

    return get_assignment_history(
        db=db,
        challenge_id=challenge_id,
    )


# ============================================================
# Reassign Challenge
# ============================================================


@router.post(
    "/{challenge_id}/reassign",
    response_model=ChallengeResponse,
)
async def reassign_challenge_to_authority(
    challenge_id: int,
    payload: ChallengeReassignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reassign a challenge from its current authority to another
    valid authority.
    """

    return reassign_challenge(
        db=db,
        challenge_id=challenge_id,
        authority_id=payload.authority_id,
        performed_by=current_user,
        reason=payload.reason,
        remarks=payload.remarks,
    )


# ============================================================
# Escalate Challenge
# ============================================================


@router.post(
    "/{challenge_id}/escalate",
    response_model=ChallengeResponse,
)
async def escalate_challenge_to_authority(
    challenge_id: int,
    payload: ChallengeEscalateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Escalate a challenge to another authority because the
    current authority cannot resolve it.
    """

    return escalate_challenge(
        db=db,
        challenge_id=challenge_id,
        authority_id=payload.authority_id,
        performed_by=current_user,
        reason=payload.reason,
        remarks=payload.remarks,
    )


# ============================================================
# Mark Challenge as Resolved
# ============================================================

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.models.challenge import Challenge, ChallengeStatus
from app.services.notification_service import notify_citizen_of_resolution
from app.models.user import UserRole as _UserRole


class ChallengeResolveRequest(BaseModel):
    resolution_summary: str = Field(
        ...,
        min_length=20,
        description="A clear description of how the issue was resolved.",
    )


RESOLVE_ALLOWED_ROLES = {
    _UserRole.SUPER_ADMIN,
    _UserRole.GOVERNMENT_OFFICER,
    _UserRole.MUNICIPALITY_OFFICER,
    _UserRole.REVIEW_OFFICER,
    _UserRole.UNIVERSITY_ADMIN,
    _UserRole.FACULTY,
}


@router.patch(
    "/{challenge_id}/resolve",
    response_model=ChallengeResponse,
)
async def resolve_challenge(
    challenge_id: int,
    payload: ChallengeResolveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark a challenge as RESOLVED and notify the citizen who
    submitted it. Allowed for government, municipality, and
    university officials.
    """

    if current_user.role not in RESOLVE_ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to resolve challenges.",
        )

    challenge = db.get(Challenge, challenge_id)

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    if challenge.status == ChallengeStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Challenge is already marked as resolved.",
        )

    # Mark resolved
    challenge.status    = ChallengeStatus.RESOLVED
    challenge.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(challenge)

    # Notify the citizen
    resolver_name = (
        f"{current_user.full_name}"
        if hasattr(current_user, "full_name") and current_user.full_name
        else current_user.email
    )

    try:
        notify_citizen_of_resolution(
            db=db,
            challenge_id=challenge.id,
            submitter_user_id=challenge.submitted_by,
            challenge_title=challenge.title,
            resolution_summary=payload.resolution_summary,
            resolved_by_name=resolver_name,
        )
    except Exception:
        # Non-fatal — challenge is already resolved
        pass

    return challenge