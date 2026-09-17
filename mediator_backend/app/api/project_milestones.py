from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project_milestone import (
    ProjectMilestoneResponse,
    ProjectMilestoneUpdate,
)
from app.services.project_milestone_service import (
    list_project_milestones,
    update_milestone,
)


router = APIRouter(
    prefix="/project-milestones",
    tags=["Project Milestones"],
)


@router.put(
    "/{milestone_id}",
    response_model=ProjectMilestoneResponse,
)
def update_project_milestone(
    milestone_id: int,
    milestone_data: ProjectMilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_milestone(
        db=db,
        milestone_id=milestone_id,
        milestone_data=milestone_data,
        current_user=current_user,
    )
    
@router.get(
    "/project/{project_id}",
    response_model=list[ProjectMilestoneResponse],
)
def get_project_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_project_milestones(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )