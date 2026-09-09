from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeResponse,
    ChallengeUpdate,
)
from app.services.challenge_service import (
    create_challenge,
    get_challenge_by_id,
    get_challenges,
    get_user_challenges,
    update_challenge,
)

from fastapi import File, UploadFile

from app.models.challenge_evidence import ChallengeEvidence
from app.schemas.evidence import EvidenceResponse
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
            detail="You can only update your own challenges.",
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


