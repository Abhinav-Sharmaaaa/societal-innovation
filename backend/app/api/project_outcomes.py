from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project_outcome import (
    ProjectOutcomeCreate,
    ProjectOutcomeResponse,
    ProjectOutcomeVerification,
)
from app.services.project_outcome_service import (
    create_project_outcome,
    list_project_outcomes,
    verify_project_outcome,
)


router = APIRouter(
    prefix="/project-outcomes",
    tags=["Project Outcomes"],
)


@router.post(
    "",
    response_model=ProjectOutcomeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_outcome(
    outcome_data: ProjectOutcomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project_outcome(
        db=db,
        outcome_data=outcome_data,
        current_user=current_user,
    )


@router.post(
    "/{outcome_id}/verify",
    response_model=ProjectOutcomeResponse,
)
def verify_outcome(
    outcome_id: int,
    verification_data: ProjectOutcomeVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return verify_project_outcome(
        db=db,
        outcome_id=outcome_id,
        verification_data=verification_data,
        current_user=current_user,
    )


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectOutcomeResponse],
)
def get_project_outcomes(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_project_outcomes(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )