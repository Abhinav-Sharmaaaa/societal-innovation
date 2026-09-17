from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.proposal_evaluation import (
    ProposalEvaluationCreate,
    ProposalEvaluationDecisionRequest,
    ProposalEvaluationResponse,
)
from app.services.proposal_evaluation_service import (
    decide_proposal,
    evaluate_proposal,
)


router = APIRouter(
    prefix="/proposal-evaluations",
    tags=["Proposal Evaluations"],
)


@router.post(
    "",
    response_model=ProposalEvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal_evaluation(
    evaluation_data: ProposalEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return evaluate_proposal(
        db=db,
        evaluation_data=evaluation_data,
        current_user=current_user,
    )
@router.post(
    "/{evaluation_id}/decision",
    response_model=ProposalEvaluationResponse,
)
def decide_proposal_evaluation(
    evaluation_id: int,
    decision_data: ProposalEvaluationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return decide_proposal(
        db=db,
        evaluation_id=evaluation_id,
        decision=decision_data.decision,
        remarks=decision_data.remarks,
        current_user=current_user,
    )