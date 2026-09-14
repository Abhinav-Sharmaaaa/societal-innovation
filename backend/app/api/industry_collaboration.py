from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.industry_collaboration import (
    IndustryCollaborationCreate,
    IndustryCollaborationDecisionRequest,
    IndustryCollaborationResponse,
)
from app.services.industry_collaboration_service import (
    decide_collaboration_proposal,
    submit_collaboration_proposal,
)

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
)
from app.models.organization import OrganizationType
from app.schemas.industry_collaboration import (
    IndustryCollaborationResponse,
)


router = APIRouter(
    prefix="/industry-collaboration",
    tags=["Industry Collaboration"],
)


@router.post(
    "",
    response_model=IndustryCollaborationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_industry_collaboration(
    collaboration_data: IndustryCollaborationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return submit_collaboration_proposal(
        db=db,
        collaboration_data=collaboration_data,
        current_user=current_user,
    )


@router.post(
    "/{collaboration_id}/decision",
    response_model=IndustryCollaborationResponse,
)
def review_industry_collaboration(
    collaboration_id: int,
    decision_data: IndustryCollaborationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return decide_collaboration_proposal(
        db=db,
        collaboration_id=collaboration_id,
        decision=decision_data.decision,
        remarks=decision_data.remarks,
        current_user=current_user,
    )
    
# ============================================================
# Industry: View My Collaboration Proposals
# ============================================================

@router.get(
    "/my",
    response_model=list[IndustryCollaborationResponse],
)
def list_my_collaborations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only industry users can view their collaborations.",
        )

    statement = (
        select(IndustryCollaborationProposal)
        .where(
            IndustryCollaborationProposal.industry_id
            == current_user.organization_id
        )
        .order_by(
            IndustryCollaborationProposal.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )
    
# ============================================================
# University: View Collaboration Proposals
# ============================================================

@router.get(
    "/university",
    response_model=list[IndustryCollaborationResponse],
)
def list_university_collaborations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only university users can view collaboration proposals.",
        )

    statement = (
        select(IndustryCollaborationProposal)
        .join(
            UniversityProposal,
            UniversityProposal.id
            == IndustryCollaborationProposal.university_proposal_id,
        )
        .where(
            UniversityProposal.university_id
            == current_user.organization_id
        )
        .order_by(
            IndustryCollaborationProposal.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )