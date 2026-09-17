from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.proposal_evaluation import (
    ProposalEvaluation,
    ProposalEvaluationDecision,
)
from app.models.university_proposal import (
    UniversityProposal,
    UniversityProposalStatus,
)
from app.models.user import User, UserRole
from app.schemas.proposal_evaluation import ProposalEvaluationCreate


WEIGHTS = {
    "technical_feasibility_score": 0.20,
    "innovation_score": 0.15,
    "cost_effectiveness_score": 0.10,
    "impact_score": 0.20,
    "timeline_score": 0.10,
    "scalability_score": 0.10,
    "research_capability_score": 0.15,
}


def calculate_overall_score(
    evaluation: ProposalEvaluationCreate,
) -> float:
    score = (
        evaluation.technical_feasibility_score
        * WEIGHTS["technical_feasibility_score"]
        + evaluation.innovation_score
        * WEIGHTS["innovation_score"]
        + evaluation.cost_effectiveness_score
        * WEIGHTS["cost_effectiveness_score"]
        + evaluation.impact_score
        * WEIGHTS["impact_score"]
        + evaluation.timeline_score
        * WEIGHTS["timeline_score"]
        + evaluation.scalability_score
        * WEIGHTS["scalability_score"]
        + evaluation.research_capability_score
        * WEIGHTS["research_capability_score"]
    )

    return round(score, 2)


def evaluate_proposal(
    db: Session,
    evaluation_data: ProposalEvaluationCreate,
    current_user: User,
) -> ProposalEvaluation:

    if current_user.role not in {
        UserRole.SUPER_ADMIN,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized government officers can evaluate proposals.",
        )

    proposal = (
        db.query(UniversityProposal)
        .filter(
            UniversityProposal.id == evaluation_data.proposal_id
        )
        .first()
    )

    if not proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University proposal not found.",
        )

    if proposal.status != UniversityProposalStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted proposals can be evaluated.",
        )

    existing = (
        db.query(ProposalEvaluation)
        .filter(
            ProposalEvaluation.proposal_id
            == evaluation_data.proposal_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This proposal has already been evaluated.",
        )

    overall_score = calculate_overall_score(
        evaluation_data
    )

    # Initial decision threshold.
    # Government can later override this through a separate
    # shortlist/rejection workflow.
    decision = ProposalEvaluationDecision.UNDER_REVIEW

    evaluation = ProposalEvaluation(
        proposal_id=proposal.id,
        evaluated_by=current_user.id,

        technical_feasibility_score=(
            evaluation_data.technical_feasibility_score
        ),
        innovation_score=evaluation_data.innovation_score,
        cost_effectiveness_score=(
            evaluation_data.cost_effectiveness_score
        ),
        impact_score=evaluation_data.impact_score,
        timeline_score=evaluation_data.timeline_score,
        scalability_score=evaluation_data.scalability_score,
        research_capability_score=(
            evaluation_data.research_capability_score
        ),

        overall_score=overall_score,
        remarks=evaluation_data.remarks,
        decision=decision,
    )

    proposal.status = UniversityProposalStatus.UNDER_EVALUATION

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation

def decide_proposal(
    db: Session,
    evaluation_id: int,
    decision: str,
    remarks: str | None,
    current_user: User,
) -> ProposalEvaluation:

    if current_user.role not in {
        UserRole.SUPER_ADMIN,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized government officers can decide proposal outcomes.",
        )

    evaluation = (
        db.query(ProposalEvaluation)
        .filter(
            ProposalEvaluation.id == evaluation_id
        )
        .first()
    )

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal evaluation not found.",
        )

    proposal = evaluation.proposal

    if decision not in {
        ProposalEvaluationDecision.SHORTLISTED.value,
        ProposalEvaluationDecision.REJECTED.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be SHORTLISTED or REJECTED.",
        )

    evaluation.decision = ProposalEvaluationDecision(
        decision
    )

    if remarks is not None:
        evaluation.remarks = remarks

    if decision == ProposalEvaluationDecision.SHORTLISTED.value:
        proposal.status = UniversityProposalStatus.SHORTLISTED

    elif decision == ProposalEvaluationDecision.REJECTED.value:
        proposal.status = UniversityProposalStatus.REJECTED

    db.commit()
    db.refresh(evaluation)

    return evaluation