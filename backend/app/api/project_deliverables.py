from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project_deliverable import (
    ProjectDeliverableCreate,
    ProjectDeliverableResponse,
    ProjectDeliverableReview,
    ProjectDeliverableSubmit,
)
from app.services.project_deliverable_service import (
    create_deliverable,
    review_deliverable,
    submit_deliverable,
)


router = APIRouter(
    prefix="/project-deliverables",
    tags=["Project Deliverables"],
)


@router.post(
    "",
    response_model=ProjectDeliverableResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_deliverable(
    deliverable_data: ProjectDeliverableCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_deliverable(
        db=db,
        deliverable_data=deliverable_data,
        current_user=current_user,
    )


@router.post(
    "/{deliverable_id}/submit",
    response_model=ProjectDeliverableResponse,
)
def submit_project_deliverable(
    deliverable_id: int,
    submission_data: ProjectDeliverableSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return submit_deliverable(
        db=db,
        deliverable_id=deliverable_id,
        submission_data=submission_data,
        current_user=current_user,
    )


@router.post(
    "/{deliverable_id}/review",
    response_model=ProjectDeliverableResponse,
)
def review_project_deliverable(
    deliverable_id: int,
    review_data: ProjectDeliverableReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return review_deliverable(
        db=db,
        deliverable_id=deliverable_id,
        review_data=review_data,
        current_user=current_user,
    )