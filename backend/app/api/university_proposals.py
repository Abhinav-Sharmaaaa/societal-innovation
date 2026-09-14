from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.dependencies import require_roles
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.university_proposal import (
    UniversityProposalCreate,
    UniversityProposalResponse,
)
from app.services.university_proposal_service import (
    create_university_proposal,
    get_rfp_proposals,
    get_university_proposal,
)
from app.models.university_proposal import (
    UniversityProposal,
    UniversityProposalStatus,
)
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/university-proposals",
    tags=["University Proposals"],
)


# ============================================================
# Submit Proposal
# ============================================================

@router.post(
    "",
    response_model=UniversityProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_proposal(
    proposal_data: UniversityProposalCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.UNIVERSITY_ADMIN,
            UserRole.FACULTY,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Submit a university proposal against an interested RFP invitation.
    """

    return create_university_proposal(
        db=db,
        proposal_data=proposal_data,
        current_user=current_user,
    )


# ============================================================
# Get Proposal
# ============================================================

@router.get(
    "/{proposal_id}",
    response_model=UniversityProposalResponse,
)
async def get_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
):
    proposal = get_university_proposal(
        db=db,
        proposal_id=proposal_id,
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University proposal not found.",
        )

    return proposal


# ============================================================
# List RFP Proposals
# ============================================================

@router.get(
    "/rfp/{rfp_id}",
    response_model=list[UniversityProposalResponse],
)
async def list_rfp_proposals(
    rfp_id: int,
    db: Session = Depends(get_db),
):
    return get_rfp_proposals(
        db=db,
        rfp_id=rfp_id,
    )
    
# ============================================================
# Industry: View Shortlisted University Proposals
# ============================================================

@router.get(
    "/shortlisted",
    response_model=list[UniversityProposalResponse],
)
async def list_shortlisted_proposals(
    current_user: User = Depends(
        require_roles(
            UserRole.INDUSTRY_ADMIN,
            UserRole.INDUSTRY_MEMBER,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return shortlisted university proposals available
    for industry collaboration.
    """

    statement = (
        select(UniversityProposal)
        .where(
            UniversityProposal.status
            == UniversityProposalStatus.SHORTLISTED
        )
        .order_by(
            UniversityProposal.updated_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )