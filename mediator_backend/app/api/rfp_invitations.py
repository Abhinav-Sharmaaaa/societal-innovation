from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db.database import get_db
from app.models.rfp_invitation import RFPInvitation
from app.models.user import User, UserRole
from app.schemas.rfp_invitation import (
    RFPInvitationCreate,
    RFPInvitationDecision,
    RFPInvitationResponse,
)
from app.services.rfp_invitation_service import (
    create_rfp_invitation,
    get_rfp_invitations,
    university_decline,
    university_interest,
)


router = APIRouter(
    prefix="/rfp-invitations",
    tags=["RFP Invitations"],
)


# ============================================================
# Government: Send Invitation
# ============================================================

@router.post(
    "",
    response_model=RFPInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation(
    invitation_data: RFPInvitationCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.GOVERNMENT_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Send an RFP invitation to a selected university.

    Government makes the final selection. AI recommendation
    metadata is stored for transparency.
    """

    return create_rfp_invitation(
        db=db,
        invitation_data=invitation_data,
        current_user=current_user,
    )


# ============================================================
# Government: View Invitations
# ============================================================

@router.get(
    "/rfp/{rfp_id}",
    response_model=list[RFPInvitationResponse],
)
async def list_invitations(
    rfp_id: int,
    db: Session = Depends(get_db),
):
    return get_rfp_invitations(
        db=db,
        rfp_id=rfp_id,
    )

# ============================================================
# University: View My Invitations
# ============================================================

@router.get(
    "/my",
    response_model=list[RFPInvitationResponse],
)
async def list_my_invitations(
    current_user: User = Depends(
        require_roles(
            UserRole.UNIVERSITY_ADMIN,
            UserRole.FACULTY,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return all RFP invitations sent to the current university.
    """

    statement = (
        select(RFPInvitation)
        .where(
            RFPInvitation.university_id
            == current_user.organization_id
        )
        .order_by(
            RFPInvitation.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )
    
# ============================================================
# University: Accept / Express Interest
# ============================================================

@router.post(
    "/{invitation_id}/interest",
    response_model=RFPInvitationResponse,
)
async def express_interest(
    invitation_id: int,
    current_user: User = Depends(
        require_roles(
            UserRole.UNIVERSITY_ADMIN,
        )
    ),
    db: Session = Depends(get_db),
):
    return university_interest(
        db=db,
        invitation_id=invitation_id,
        current_user=current_user,
    )


# ============================================================
# University: Decline
# ============================================================

@router.post(
    "/{invitation_id}/decline",
    response_model=RFPInvitationResponse,
)
async def decline_invitation(
    invitation_id: int,
    decision: RFPInvitationDecision,
    current_user: User = Depends(
        require_roles(
            UserRole.UNIVERSITY_ADMIN,
        )
    ),
    db: Session = Depends(get_db),
):
    return university_decline(
        db=db,
        invitation_id=invitation_id,
        current_user=current_user,
        reason=decision.reason,
    )