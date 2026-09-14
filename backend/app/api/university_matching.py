from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from fastapi import Depends

from app.ai.matching_schemas import (
    UniversityMatchingResponse,
)
from app.ai.university_matching_service import (
    match_universities_for_rfp,
)
from app.api.dependencies import require_roles
from app.db.database import get_db
from app.models.user import User, UserRole


router = APIRouter(
    prefix="/rfps",
    tags=["University Matching"],
)


# ============================================================
# Match Universities
# ============================================================

@router.post(
    "/{rfp_id}/match-universities",
    response_model=UniversityMatchingResponse,
)
async def match_universities(
    rfp_id: int,
    current_user: User = Depends(
        require_roles(
            UserRole.SUPER_ADMIN,
            UserRole.GOVERNMENT_OFFICER,
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Generate the Top 3 university recommendations
    for an RFP.

    AI/ranking provides recommendations.
    Government retains final authority over invitations.
    """

    try:
        return match_universities_for_rfp(
            db=db,
            rfp_id=rfp_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )