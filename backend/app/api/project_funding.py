from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project_funding import (
    ProjectFundingApproval,
    ProjectFundingCreate,
    ProjectFundingResponse,
    ProjectFundingSummary,
)
from app.services.project_funding_service import (
    approve_funding_transaction,
    complete_funding_transaction,
    create_funding_transaction,
    get_project_funding_summary,
    list_project_funding_transactions,
)


router = APIRouter(
    prefix="/project-funding",
    tags=["Project Funding"],
)


@router.post(
    "",
    response_model=ProjectFundingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_funding(
    funding_data: ProjectFundingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_funding_transaction(
        db=db,
        funding_data=funding_data,
        current_user=current_user,
    )


@router.post(
    "/{transaction_id}/approve",
    response_model=ProjectFundingResponse,
)
def approve_project_funding(
    transaction_id: int,
    approval_data: ProjectFundingApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return approve_funding_transaction(
        db=db,
        transaction_id=transaction_id,
        approval_data=approval_data,
        current_user=current_user,
    )


@router.post(
    "/{transaction_id}/complete",
    response_model=ProjectFundingResponse,
)
def complete_project_funding(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return complete_funding_transaction(
        db=db,
        transaction_id=transaction_id,
        current_user=current_user,
    )


@router.get(
    "/project/{project_id}/summary",
    response_model=ProjectFundingSummary,
)
def project_funding_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_project_funding_summary(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    
@router.get(
    "/project/{project_id}/transactions",
    response_model=list[ProjectFundingResponse],
)
def project_funding_transactions(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_project_funding_transactions(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )