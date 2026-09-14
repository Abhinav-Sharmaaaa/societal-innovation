from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.innovation_opportunity import (
    InnovationOpportunity,
    InnovationOpportunityStatus,
)
from app.models.rfp import RFP, RFPStatus
from app.models.user import User
from app.schemas.rfp import RFPCreate


def create_rfp(
    db: Session,
    rfp_data: RFPCreate,
    current_user: User,
) -> RFP:

    opportunity = db.get(
        InnovationOpportunity,
        rfp_data.innovation_opportunity_id,
    )

    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Innovation opportunity not found.",
        )

    if opportunity.status not in {
        InnovationOpportunityStatus.APPROVED,
        InnovationOpportunityStatus.ACTIVE,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "An RFP can only be created for an "
                "approved or active innovation opportunity."
            ),
        )

    existing = db.scalars(
        select(RFP).where(
            RFP.innovation_opportunity_id
            == opportunity.id
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An RFP already exists for this "
                "innovation opportunity."
            ),
        )

    rfp = RFP(
        innovation_opportunity_id=opportunity.id,
        created_by=current_user.id,
        title=rfp_data.title,
        description=rfp_data.description,
        objectives=rfp_data.objectives,
        technical_requirements=(
            rfp_data.technical_requirements
        ),
        expected_outcomes=(
            rfp_data.expected_outcomes
        ),
        estimated_budget=rfp_data.estimated_budget,
        expected_duration_days=(
            rfp_data.expected_duration_days
        ),
        proposal_deadline=rfp_data.proposal_deadline,
        status=RFPStatus.DRAFT,
        is_active=True,
    )

    db.add(rfp)

    # Innovation Opportunity has now entered the RFP stage.
    opportunity.status = (
        InnovationOpportunityStatus.RFP_CREATED
    )

    db.commit()
    db.refresh(rfp)

    return rfp


def get_rfp(
    db: Session,
    rfp_id: int,
) -> RFP | None:

    return db.get(RFP, rfp_id)


def publish_rfp(
    db: Session,
    rfp_id: int,
    current_user: User,
) -> RFP:

    rfp = db.get(
        RFP,
        rfp_id,
    )

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    if rfp.status != RFPStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft RFPs can be published.",
        )

    if rfp.proposal_deadline is not None:
        now = datetime.now(timezone.utc)

        if rfp.proposal_deadline <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Proposal deadline must be in the future."
                ),
            )

    rfp.status = RFPStatus.PUBLISHED
    rfp.published_at = datetime.now(timezone.utc)

    rfp.innovation_opportunity.status = (
        InnovationOpportunityStatus.ACTIVE
    )

    db.commit()
    db.refresh(rfp)

    return rfp


def close_rfp(
    db: Session,
    rfp_id: int,
    current_user: User,
) -> RFP:

    rfp = db.get(
        RFP,
        rfp_id,
    )

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    if rfp.status != RFPStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published RFPs can be closed.",
        )

    rfp.status = RFPStatus.CLOSED
    rfp.closed_at = datetime.now(timezone.utc)
    rfp.is_active = False

    db.commit()
    db.refresh(rfp)

    return rfp