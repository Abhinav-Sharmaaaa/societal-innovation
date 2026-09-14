from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.models.innovation_opportunity import (
    InnovationOpportunity,
    InnovationOpportunityStatus,
)
from app.models.organization import Organization
from app.models.user import User
from app.schemas.innovation_opportunity import (
    InnovationOpportunityCreate,
)


# ============================================================
# Create Innovation Opportunity
# ============================================================

def create_innovation_opportunity(
    db: Session,
    opportunity_data: InnovationOpportunityCreate,
    current_user: User,
) -> InnovationOpportunity:

    # --------------------------------------------------------
    # Validate challenge
    # --------------------------------------------------------

    challenge = db.get(
        Challenge,
        opportunity_data.challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    # --------------------------------------------------------
    # Challenge must require innovation
    # --------------------------------------------------------

    if not challenge.innovation_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This challenge is not currently marked "
                "as requiring innovation."
            ),
        )

    # --------------------------------------------------------
    # Prevent duplicate opportunity
    # --------------------------------------------------------

    existing = db.scalars(
        select(InnovationOpportunity).where(
            InnovationOpportunity.challenge_id
            == opportunity_data.challenge_id
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An innovation opportunity already exists "
                "for this challenge."
            ),
        )

    # --------------------------------------------------------
    # Validate sponsoring organization
    # --------------------------------------------------------

    organization = db.get(
        Organization,
        opportunity_data.sponsoring_organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sponsoring organization not found.",
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sponsoring organization is inactive.",
        )

    # --------------------------------------------------------
    # Organization must match challenge jurisdiction
    # --------------------------------------------------------

    if (
        challenge.state
        and organization.state
        and challenge.state != organization.state
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Sponsoring organization is outside the "
                "challenge state jurisdiction."
            ),
        )

    if (
        challenge.district
        and organization.district
        and challenge.district != organization.district
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Sponsoring organization is outside the "
                "challenge district jurisdiction."
            ),
        )

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------

    opportunity = InnovationOpportunity(
        challenge_id=challenge.id,
        sponsoring_organization_id=organization.id,
        created_by=current_user.id,
        title=opportunity_data.title,
        problem_statement=(
            opportunity_data.problem_statement
        ),
        objectives=opportunity_data.objectives,
        technical_requirements=(
            opportunity_data.technical_requirements
        ),
        expected_outcomes=(
            opportunity_data.expected_outcomes
        ),
        estimated_budget=(
            opportunity_data.estimated_budget
        ),
        expected_duration_days=(
            opportunity_data.expected_duration_days
        ),
        proposal_deadline=(
            opportunity_data.proposal_deadline
        ),
        status=InnovationOpportunityStatus.DRAFT,
        is_active=True,
    )

    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)

    return opportunity


# ============================================================
# Approve Innovation Opportunity
# ============================================================

def approve_innovation_opportunity(
    db: Session,
    opportunity_id: int,
    current_user: User,
) -> InnovationOpportunity:

    opportunity = db.get(
        InnovationOpportunity,
        opportunity_id,
    )

    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Innovation opportunity not found.",
        )

    if (
        opportunity.status
        != InnovationOpportunityStatus.DRAFT
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only draft innovation opportunities "
                "can be approved."
            ),
        )

    now = datetime.now(timezone.utc)

    opportunity.status = (
        InnovationOpportunityStatus.APPROVED
    )
    opportunity.approved_by = current_user.id
    opportunity.approved_at = now

    db.commit()
    db.refresh(opportunity)

    return opportunity


# ============================================================
# Get Opportunity
# ============================================================

def get_innovation_opportunity(
    db: Session,
    opportunity_id: int,
) -> InnovationOpportunity | None:

    return db.get(
        InnovationOpportunity,
        opportunity_id,
    )