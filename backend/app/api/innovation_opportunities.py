from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.db.database import get_db
from app.models.innovation_opportunity import (
    InnovationOpportunity,
)
from app.models.user import User, UserRole
from app.schemas.innovation_opportunity import (
    InnovationOpportunityCreate,
    InnovationOpportunityResponse,
)
from app.services.innovation_opportunity_service import (
    approve_innovation_opportunity,
    create_innovation_opportunity,
    get_innovation_opportunity,
)


router = APIRouter(
    prefix="/innovation-opportunities",
    tags=["Innovation Opportunities"],
)


# ============================================================
# Create
# ============================================================

@router.post(
    "",
    response_model=InnovationOpportunityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_opportunity(
    opportunity_data: InnovationOpportunityCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.REVIEW_OFFICER,
            UserRole.GOVERNMENT_OFFICER,
            UserRole.MUNICIPALITY_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Create an innovation opportunity from an eligible challenge.
    """

    return create_innovation_opportunity(
        db=db,
        opportunity_data=opportunity_data,
        current_user=current_user,
    )


# ============================================================
# Get
# ============================================================

@router.get(
    "/{opportunity_id}",
    response_model=InnovationOpportunityResponse,
)
async def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve an innovation opportunity.
    """

    opportunity = get_innovation_opportunity(
        db=db,
        opportunity_id=opportunity_id,
    )

    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Innovation opportunity not found.",
        )

    return opportunity


# ============================================================
# Approve
# ============================================================

@router.post(
    "/{opportunity_id}/approve",
    response_model=InnovationOpportunityResponse,
)
async def approve_opportunity(
    opportunity_id: int,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.REVIEW_OFFICER,
            UserRole.GOVERNMENT_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Approve a draft innovation opportunity.

    Approval is required before an RFP can be created.
    """

    return approve_innovation_opportunity(
        db=db,
        opportunity_id=opportunity_id,
        current_user=current_user,
    )