from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.university_matching_service import (
    match_universities_for_rfp,
)
from app.models.organization import (
    Organization,
    OrganizationType,
)
from app.models.rfp import RFP, RFPStatus
from app.models.rfp_invitation import (
    RFPInvitation,
    RFPInvitationStatus,
)
from app.models.user import User
from app.schemas.rfp_invitation import (
    RFPInvitationCreate,
)


# ============================================================
# Create Invitation
# ============================================================

def create_rfp_invitation(
    db: Session,
    invitation_data: RFPInvitationCreate,
    current_user: User,
) -> RFPInvitation:

    rfp = db.get(
        RFP,
        invitation_data.rfp_id,
    )

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    if rfp.status != RFPStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Universities can only be invited "
                "after the RFP is published."
            ),
        )

    university = db.get(
        Organization,
        invitation_data.university_id,
    )

    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found.",
        )

    if university.organization_type != OrganizationType.UNIVERSITY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected organization is not a university.",
        )

    if not university.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="University is inactive.",
        )

    # --------------------------------------------------------
    # Prevent duplicate invitation
    # --------------------------------------------------------

    existing = db.scalars(
        select(RFPInvitation).where(
            RFPInvitation.rfp_id
            == invitation_data.rfp_id,
            RFPInvitation.university_id
            == invitation_data.university_id,
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This university has already been invited "
                "to this RFP."
            ),
        )

    # --------------------------------------------------------
    # Get current AI recommendation
    # --------------------------------------------------------

    matching = match_universities_for_rfp(
        db=db,
        rfp_id=rfp.id,
    )

    recommendation = next(
        (
            item
            for item in matching.recommendations
            if item.organization_id
            == university.id
        ),
        None,
    )

    invitation = RFPInvitation(
        rfp_id=rfp.id,
        university_id=university.id,
        invited_by=current_user.id,
        recommendation_rank=(
            recommendation.rank
            if recommendation
            else None
        ),
        match_score=(
            recommendation.score
            if recommendation
            else None
        ),
        status=RFPInvitationStatus.INVITED,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


# ============================================================
# List RFP Invitations
# ============================================================

def get_rfp_invitations(
    db: Session,
    rfp_id: int,
) -> list[RFPInvitation]:

    rfp = db.get(RFP, rfp_id)

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    statement = (
        select(RFPInvitation)
        .where(
            RFPInvitation.rfp_id == rfp_id
        )
        .order_by(
            RFPInvitation.recommendation_rank,
            RFPInvitation.invited_at,
        )
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# University: Mark Interested
# ============================================================

def university_interest(
    db: Session,
    invitation_id: int,
    current_user: User,
) -> RFPInvitation:

    invitation = db.get(
        RFPInvitation,
        invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP invitation not found.",
        )

    if current_user.organization_id != (
        invitation.university_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to respond "
                "to this university invitation."
            ),
        )

    if invitation.status not in {
        RFPInvitationStatus.INVITED,
        RFPInvitationStatus.VIEWED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This invitation can no longer "
                "be marked as interested."
            ),
        )

    invitation.status = (
        RFPInvitationStatus.INTERESTED
    )
    invitation.responded_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(invitation)

    return invitation


# ============================================================
# University: Decline
# ============================================================

def university_decline(
    db: Session,
    invitation_id: int,
    current_user: User,
    reason: str | None = None,
) -> RFPInvitation:

    invitation = db.get(
        RFPInvitation,
        invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP invitation not found.",
        )

    if current_user.organization_id != (
        invitation.university_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to respond "
                "to this university invitation."
            ),
        )

    if invitation.status not in {
        RFPInvitationStatus.INVITED,
        RFPInvitationStatus.VIEWED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This invitation can no longer "
                "be declined."
            ),
        )

    invitation.status = (
        RFPInvitationStatus.DECLINED
    )
    invitation.response_reason = reason
    invitation.responded_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(invitation)

    return invitation