from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project_risk import (
    ProjectRiskActionRequest,
    ProjectRiskResponse,
)
from app.services.project_risk_service import (
    run_project_risk_assessment,
    update_project_risk_status,
)


router = APIRouter(
    prefix="/project-risks",
    tags=["Project Risks"],
)


@router.post(
    "/project/{project_id}/assess",
    response_model=ProjectRiskResponse,
)
def assess_project_risk(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return run_project_risk_assessment(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    
@router.post(
    "/{risk_id}/action",
    response_model=ProjectRiskResponse,
)
def manage_project_risk(
    risk_id: int,
    action_data: ProjectRiskActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_project_risk_status(
        db=db,
        risk_id=risk_id,
        action=action_data.action,
        remarks=action_data.remarks,
        current_user=current_user,
    )