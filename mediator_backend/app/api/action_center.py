from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.action_center import (
    ActionCenterResponse,
)
from app.services.action_center_service import (
    get_action_center,
)


router = APIRouter(
    prefix="/action-center",
    tags=["Action Center"],
)


@router.get(
    "",
    response_model=ActionCenterResponse,
)
def action_center(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_action_center(
        db=db,
        current_user=current_user,
    )