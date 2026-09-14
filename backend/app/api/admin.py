from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    OfficialUserCreate,
    UserResponse,
)
from app.services.admin_user_service import (
    create_official_user,
)


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


# ============================================================
# SUPER_ADMIN Guard
# ============================================================

def require_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow only SUPER_ADMIN users.
    """

    if current_user.role != UserRole.SUPER_ADMIN:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SUPER_ADMIN privileges required.",
        )

    return current_user


# ============================================================
# Create Official User
# ============================================================

@router.post(
    "/users",
    response_model=UserResponse,
)
async def create_official_account(
    user_data: OfficialUserCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Create an official user and associate the user with an
    organization.

    Only SUPER_ADMIN can create official accounts.
    """

    return create_official_user(
        db=db,
        user_data=user_data,
    )