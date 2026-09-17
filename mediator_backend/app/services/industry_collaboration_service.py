from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
    IndustryCollaborationStatus,
)
from app.models.organization import (
    Organization,
    OrganizationType,
)
from app.models.university_proposal import (
    UniversityProposal,
    UniversityProposalStatus,
)
from app.models.user import User, UserRole
from app.schemas.industry_collaboration import (
    IndustryCollaborationCreate,
)


def submit_collaboration_proposal(
    db: Session,
    collaboration_data: IndustryCollaborationCreate,
    current_user: User,
) -> IndustryCollaborationProposal:

    # ---------------------------------------------------------
    # 1. Validate user role
    # ---------------------------------------------------------
    if current_user.role not in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only industry users can submit collaboration proposals.",
        )

    # ---------------------------------------------------------
    # 2. Validate organization association
    # ---------------------------------------------------------
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Industry user is not associated with an organization.",
        )

    # ---------------------------------------------------------
    # 3. Load and validate industry organization
    # ---------------------------------------------------------
    industry = (
        db.query(Organization)
        .filter(
            Organization.id == current_user.organization_id
        )
        .first()
    )

    if not industry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry organization not found.",
        )

    if industry.organization_type != OrganizationType.INDUSTRY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only industry organizations can submit collaboration proposals.",
        )

    if not industry.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This industry organization is inactive.",
        )

    # ---------------------------------------------------------
    # 4. Load university proposal
    # ---------------------------------------------------------
    university_proposal = (
        db.query(UniversityProposal)
        .filter(
            UniversityProposal.id
            == collaboration_data.university_proposal_id
        )
        .first()
    )

    if not university_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University proposal not found.",
        )

    # ---------------------------------------------------------
    # 5. Industry collaboration only for shortlisted proposals
    # ---------------------------------------------------------
    if (
        university_proposal.status
        != UniversityProposalStatus.SHORTLISTED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Industry collaboration is available only "
                "for shortlisted university proposals."
            ),
        )

    # ---------------------------------------------------------
    # 6. Prevent duplicate proposal from same industry
    # ---------------------------------------------------------
    existing = (
        db.query(IndustryCollaborationProposal)
        .filter(
            IndustryCollaborationProposal.university_proposal_id
            == university_proposal.id,
            IndustryCollaborationProposal.industry_id
            == industry.id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This industry has already submitted a collaboration "
                "proposal for this university proposal."
            ),
        )

    # ---------------------------------------------------------
    # 7. Create collaboration proposal
    # ---------------------------------------------------------
    collaboration = IndustryCollaborationProposal(
        university_proposal_id=university_proposal.id,
        industry_id=industry.id,
        submitted_by=current_user.id,

        title=collaboration_data.title,
        collaboration_description=(
            collaboration_data.collaboration_description
        ),

        funding_amount=collaboration_data.funding_amount,

        technical_mentorship=(
            collaboration_data.technical_mentorship
        ),
        industry_experts=collaboration_data.industry_experts,
        infrastructure_resources=(
            collaboration_data.infrastructure_resources
        ),
        technology_support=(
            collaboration_data.technology_support
        ),
        internship_support=(
            collaboration_data.internship_support
        ),
        pilot_deployment_support=(
            collaboration_data.pilot_deployment_support
        ),
        commercialization_support=(
            collaboration_data.commercialization_support
        ),

        proposed_duration_days=(
            collaboration_data.proposed_duration_days
        ),
        
        response_deadline=(
            collaboration_data.response_deadline
        ),

        additional_terms=(
            collaboration_data.additional_terms
        ),

        status=IndustryCollaborationStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
    )

    # ---------------------------------------------------------
    # 8. Save
    # ---------------------------------------------------------
    db.add(collaboration)
    db.commit()
    db.refresh(collaboration)

    return collaboration


def decide_collaboration_proposal(
    db: Session,
    collaboration_id: int,
    decision: str,
    remarks: str | None,
    current_user: User,
) -> IndustryCollaborationProposal:

    # ---------------------------------------------------------
    # 1. Validate university role
    # ---------------------------------------------------------
    if current_user.role not in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only university users can review "
                "industry collaboration proposals."
            ),
        )

    # ---------------------------------------------------------
    # 2. Load collaboration proposal
    # ---------------------------------------------------------
    collaboration = (
        db.query(IndustryCollaborationProposal)
        .filter(
            IndustryCollaborationProposal.id == collaboration_id
        )
        .first()
    )

    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry collaboration proposal not found.",
        )

    # ---------------------------------------------------------
    # 3. Verify associated university proposal
    # ---------------------------------------------------------
    university_proposal = collaboration.university_proposal

    if not university_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated university proposal not found.",
        )

    # ---------------------------------------------------------
    # 4. Verify university ownership
    # ---------------------------------------------------------
    if current_user.organization_id != university_proposal.university_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to review "
                "this collaboration proposal."
            ),
        )

    # ---------------------------------------------------------
    # 5. Validate decision
    # ---------------------------------------------------------
    allowed_decisions = {
        IndustryCollaborationStatus.ACCEPTED.value,
        IndustryCollaborationStatus.REJECTED.value,
        IndustryCollaborationStatus.MODIFICATION_REQUESTED.value,
    }

    if decision not in allowed_decisions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Decision must be ACCEPTED, REJECTED, "
                "or MODIFICATION_REQUESTED."
            ),
        )

    # ---------------------------------------------------------
    # 6. Validate current state
    # ---------------------------------------------------------
    allowed_current_statuses = {
        IndustryCollaborationStatus.SUBMITTED,
        IndustryCollaborationStatus.UNDER_REVIEW,
        IndustryCollaborationStatus.MODIFICATION_REQUESTED,
    }

    if collaboration.status not in allowed_current_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This collaboration proposal cannot be reviewed "
                "in its current state."
            ),
        )

    # ---------------------------------------------------------
    # 7. Apply university decision
    # ---------------------------------------------------------
    collaboration.status = IndustryCollaborationStatus(decision)
    collaboration.reviewed_at = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 8. Store review remarks
    # ---------------------------------------------------------
    if remarks:
        existing_terms = collaboration.additional_terms or ""

        collaboration.additional_terms = (
            f"{existing_terms}\n\n"
            f"University Review: {remarks}"
        ).strip()

    # ---------------------------------------------------------
    # 9. Save
    # ---------------------------------------------------------
    db.commit()
    db.refresh(collaboration)

    return collaboration