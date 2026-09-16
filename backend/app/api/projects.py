from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
)
from app.services.project_service import (
    create_project,
    get_project,
    list_projects,
)


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_endpoint(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project(
        db=db,
        project_data=project_data,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_projects(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_project(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )