from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db.database import get_db
from app.models.rfp import RFP, RFPStatus
from app.models.user import User, UserRole
from app.schemas.rfp import (
    RFPCreate,
    RFPResponse,
)
from app.services.rfp_service import (
    close_rfp,
    create_rfp,
    get_rfp,
    list_rfps,
    publish_rfp,
)


router = APIRouter(
    prefix="/rfps",
    tags=["RFPs"],
)


# ============================================================
# Create RFP
# ============================================================

@router.post(
    "",
    response_model=RFPResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_rfp(
    rfp_data: RFPCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.GOVERNMENT_OFFICER,
            UserRole.MUNICIPALITY_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Create an RFP from an approved innovation opportunity.
    """

    return create_rfp(
        db=db,
        rfp_data=rfp_data,
        current_user=current_user,
    )


# ============================================================
# List RFPs
# ============================================================

@router.get(
    "",
    response_model=list[RFPResponse],
)
async def list_all_rfps(
    status: RFPStatus | None = Query(
        default=None,
        description="Filter by RFP status",
    ),
    db: Session = Depends(get_db),
):
    """
    List all RFPs, optionally filtered by status.
    Ordered newest first.
    """

    return list_rfps(
        db=db,
        status_filter=status,
    )


# ============================================================
# Get RFP
# ============================================================

@router.get(
    "/{rfp_id}",
    response_model=RFPResponse,
)
async def get_rfp_by_id(
    rfp_id: int,
    db: Session = Depends(get_db),
):
    rfp = get_rfp(
        db=db,
        rfp_id=rfp_id,
    )

    if rfp is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found.",
        )

    return rfp


# ============================================================
# Publish RFP
# ============================================================

@router.post(
    "/{rfp_id}/publish",
    response_model=RFPResponse,
)
async def publish_existing_rfp(
    rfp_id: int,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.GOVERNMENT_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    return publish_rfp(
        db=db,
        rfp_id=rfp_id,
        current_user=current_user,
    )


# ============================================================
# Close RFP
# ============================================================

@router.post(
    "/{rfp_id}/close",
    response_model=RFPResponse,
)
async def close_existing_rfp(
    rfp_id: int,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.GOVERNMENT_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    return close_rfp(
        db=db,
        rfp_id=rfp_id,
        current_user=current_user,
    )