from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import OrganizationType
from app.models.rfp import RFP, RFPStatus
from app.models.rfp_invitation import (
    RFPInvitation,
    RFPInvitationStatus,
)
from app.models.university_proposal import (
    UniversityProposal,
    UniversityProposalStatus,
)
from app.models.user import User, UserRole
from app.schemas.university_proposal import (
    UniversityProposalCreate,
)


# ============================================================
# Create University Proposal
# ============================================================

def create_university_proposal(
    db: Session,
    proposal_data: UniversityProposalCreate,
    current_user: User,
) -> UniversityProposal:

    # --------------------------------------------------------
    # Current user must belong to a university
    # --------------------------------------------------------

    university = current_user.organization

    if university is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "University user is not associated "
                "with an organization."
            ),
        )

    if (
        university.organization_type
        != OrganizationType.UNIVERSITY
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only university users can submit "
                "university proposals."
            ),
        )

    # --------------------------------------------------------
    # User role
    # --------------------------------------------------------

    if current_user.role not in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only UNIVERSITY_ADMIN or FACULTY users "
                "can submit proposals."
            ),
        )

    # --------------------------------------------------------
    # Get invitation
    # --------------------------------------------------------

    invitation = db.get(
        RFPInvitation,
        proposal_data.invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP invitation not found.",
        )

    # --------------------------------------------------------
    # Verify invitation belongs to current university
    # --------------------------------------------------------

    if (
        invitation.university_id
        != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This invitation does not belong "
                "to your university."
            ),
        )

    # --------------------------------------------------------
    # Invitation must be interested
    # --------------------------------------------------------

    if invitation.status != RFPInvitationStatus.INTERESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The university must express interest "
                "in the RFP before submitting a proposal."
            ),
        )

    # --------------------------------------------------------
    # Get RFP
    # --------------------------------------------------------

    rfp = db.get(
        RFP,
        invitation.rfp_id,
    )

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    # --------------------------------------------------------
    # RFP must be published
    # --------------------------------------------------------

    if rfp.status != RFPStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Proposals can only be submitted "
                "for published RFPs."
            ),
        )

    # --------------------------------------------------------
    # Check proposal deadline
    # --------------------------------------------------------

    if rfp.proposal_deadline is not None:
        now = datetime.now(timezone.utc)

        deadline = rfp.proposal_deadline

        # Normalize a naive datetime if one somehow exists.
        if deadline.tzinfo is None:
            deadline = deadline.replace(
                tzinfo=timezone.utc
            )

        if now >= deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The proposal deadline has passed.",
            )

    # --------------------------------------------------------
    # Prevent duplicate proposal
    # --------------------------------------------------------

    existing = db.scalars(
        select(UniversityProposal).where(
            UniversityProposal.invitation_id
            == invitation.id
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A proposal has already been submitted "
                "for this RFP invitation."
            ),
        )

    # --------------------------------------------------------
    # Create proposal
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    proposal = UniversityProposal(
        rfp_id=rfp.id,
        invitation_id=invitation.id,
        university_id=current_user.organization_id,
        submitted_by=current_user.id,
        title=proposal_data.title,
        solution=proposal_data.solution,
        technical_approach=(
            proposal_data.technical_approach
        ),
        research_methodology=(
            proposal_data.research_methodology
        ),
        required_resources=(
            proposal_data.required_resources
        ),
        estimated_cost=proposal_data.estimated_cost,
        expected_timeline_days=(
            proposal_data.expected_timeline_days
        ),
        faculty_team=proposal_data.faculty_team,
        expected_outcomes=(
            proposal_data.expected_outcomes
        ),
        technology_requirements=(
            proposal_data.technology_requirements
        ),
        status=UniversityProposalStatus.SUBMITTED,
        submitted_at=now,
    )

    db.add(proposal)

    # --------------------------------------------------------
    # Update invitation
    # --------------------------------------------------------

    invitation.status = (
        RFPInvitationStatus.PROPOSAL_SUBMITTED
    )

    invitation.responded_at = now

    db.commit()
    db.refresh(proposal)

    return proposal


# ============================================================
# Get Proposal
# ============================================================

def get_university_proposal(
    db: Session,
    proposal_id: int,
) -> UniversityProposal | None:

    return db.get(
        UniversityProposal,
        proposal_id,
    )


# ============================================================
# List RFP Proposals
# ============================================================

def get_rfp_proposals(
    db: Session,
    rfp_id: int,
) -> list[UniversityProposal]:

    rfp = db.get(
        RFP,
        rfp_id,
    )

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    statement = (
        select(UniversityProposal)
        .where(
            UniversityProposal.rfp_id == rfp_id
        )
        .order_by(
            UniversityProposal.created_at
        )
    )

    return list(
        db.scalars(statement).all()
    )