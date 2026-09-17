from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
    IndustryCollaborationStatus,
)
from app.models.project import (
    Project,
    ProjectStatus,
)
from app.models.project_deliverable import (
    ProjectDeliverable,
    ProjectDeliverableStatus,
)
from app.models.project_funding import (
    FundingTransactionStatus,
    FundingTransactionType,
    ProjectFundingTransaction,
)
from app.models.project_milestone import (
    ProjectMilestone,
    ProjectMilestoneStatus,
)
from app.models.project_outcome import (
    ProjectOutcome,
    ProjectOutcomeStatus,
)
from app.models.reputation_score import ReputationScore
from app.models.user import User


def get_industry_dashboard(
    db: Session,
    current_user: User,
) -> dict:

    organization_id = current_user.organization_id

    if organization_id is None:
        raise ValueError(
            "Industry user is not associated with an organization."
        )

    # =========================================================
    # COLLABORATION PROPOSALS
    # =========================================================

    collaboration_total = (
        db.query(
            func.count(
                IndustryCollaborationProposal.id
            )
        )
        .filter(
            IndustryCollaborationProposal.industry_id
            == organization_id
        )
        .scalar()
        or 0
    )

    collaboration_draft = (
        db.query(
            func.count(
                IndustryCollaborationProposal.id
            )
        )
        .filter(
            IndustryCollaborationProposal.industry_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.DRAFT,
        )
        .scalar()
        or 0
    )

    collaboration_submitted = (
        db.query(
            func.count(
                IndustryCollaborationProposal.id
            )
        )
        .filter(
            IndustryCollaborationProposal.industry_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.SUBMITTED,
        )
        .scalar()
        or 0
    )

    collaboration_under_review = (
        db.query(
            func.count(
                IndustryCollaborationProposal.id
            )
        )
        .filter(
            IndustryCollaborationProposal.industry_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.UNDER_REVIEW,
        )
        .scalar()
        or 0
    )

    collaboration_accepted = (
        db.query(
            func.count(
                IndustryCollaborationProposal.id
            )
        )
        .filter(
            IndustryCollaborationProposal.industry_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.ACCEPTED,
        )
        .scalar()
        or 0
    )

    collaboration_rejected = (
        db.query(
            func.count(
                IndustryCollaborationProposal.id
            )
        )
        .filter(
            IndustryCollaborationProposal.industry_id
            == organization_id,
            IndustryCollaborationProposal.status
            == IndustryCollaborationStatus.REJECTED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # PROJECTS
    # =========================================================

    project_total = (
        db.query(func.count(Project.id))
        .filter(
            Project.industry_id == organization_id
        )
        .scalar()
        or 0
    )

    project_planning = (
        db.query(func.count(Project.id))
        .filter(
            Project.industry_id == organization_id,
            Project.status
            == ProjectStatus.PLANNING,
        )
        .scalar()
        or 0
    )

    project_active = (
        db.query(func.count(Project.id))
        .filter(
            Project.industry_id == organization_id,
            Project.status
            == ProjectStatus.ACTIVE,
        )
        .scalar()
        or 0
    )

    project_on_hold = (
        db.query(func.count(Project.id))
        .filter(
            Project.industry_id == organization_id,
            Project.status
            == ProjectStatus.ON_HOLD,
        )
        .scalar()
        or 0
    )

    project_completed = (
        db.query(func.count(Project.id))
        .filter(
            Project.industry_id == organization_id,
            Project.status
            == ProjectStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # MILESTONES
    # =========================================================

    milestone_total = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id
        )
        .scalar()
        or 0
    )

    milestone_completed = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectMilestone.status
            == ProjectMilestoneStatus.COMPLETED,
        )
        .scalar()
        or 0
    )

    milestone_delayed = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectMilestone.status
            == ProjectMilestoneStatus.DELAYED,
        )
        .scalar()
        or 0
    )

    milestone_blocked = (
        db.query(func.count(ProjectMilestone.id))
        .join(
            Project,
            ProjectMilestone.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectMilestone.status
            == ProjectMilestoneStatus.BLOCKED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # DELIVERABLES
    # =========================================================

    deliverable_total = (
        db.query(func.count(ProjectDeliverable.id))
        .join(
            Project,
            ProjectDeliverable.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id
        )
        .scalar()
        or 0
    )

    deliverable_approved = (
        db.query(func.count(ProjectDeliverable.id))
        .join(
            Project,
            ProjectDeliverable.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectDeliverable.status
            == ProjectDeliverableStatus.APPROVED,
        )
        .scalar()
        or 0
    )

    deliverable_rejected = (
        db.query(func.count(ProjectDeliverable.id))
        .join(
            Project,
            ProjectDeliverable.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectDeliverable.status
            == ProjectDeliverableStatus.REJECTED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # FUNDING CONTRIBUTIONS
    # =========================================================

    funding_transactions = (
        db.query(ProjectFundingTransaction)
        .join(
            Project,
            ProjectFundingTransaction.project_id
            == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectFundingTransaction.status
            == FundingTransactionStatus.COMPLETED,
        )
        .all()
    )

    allocated = 0.0
    disbursed = 0.0
    utilized = 0.0
    refunded = 0.0

    for transaction in funding_transactions:

        amount = float(transaction.amount or 0)

        if transaction.transaction_type == (
            FundingTransactionType.ALLOCATION
        ):
            allocated += amount

        elif transaction.transaction_type == (
            FundingTransactionType.DISBURSEMENT
        ):
            disbursed += amount

        elif transaction.transaction_type == (
            FundingTransactionType.UTILIZATION
        ):
            utilized += amount

        elif transaction.transaction_type == (
            FundingTransactionType.REFUND
        ):
            refunded += amount

    # =========================================================
    # VERIFIED OUTCOMES / BENEFICIARIES
    # =========================================================

    verified_outcomes = (
        db.query(func.count(ProjectOutcome.id))
        .join(
            Project,
            ProjectOutcome.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED,
        )
        .scalar()
        or 0
    )

    beneficiaries = (
        db.query(
            func.coalesce(
                func.sum(
                    ProjectOutcome.beneficiary_count
                ),
                0,
            )
        )
        .join(
            Project,
            ProjectOutcome.project_id == Project.id,
        )
        .filter(
            Project.industry_id == organization_id,
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED,
        )
        .scalar()
        or 0
    )

    # =========================================================
    # PROJECT PROGRESS
    # =========================================================

    average_project_progress = (
        db.query(
            func.coalesce(
                func.avg(
                    Project.progress_percentage
                ),
                0,
            )
        )
        .filter(
            Project.industry_id == organization_id
        )
        .scalar()
        or 0
    )

    # =========================================================
    # REPUTATION
    # =========================================================

    reputation = (
        db.query(ReputationScore)
        .filter(
            ReputationScore.organization_id
            == organization_id,
        )
        .first()
    )

    reputation_points = (
        reputation.total_points
        if reputation
        else 0
    )

    reputation_contributions = (
        reputation.contribution_count
        if reputation
        else 0
    )

    # =========================================================
    # RESPONSE
    # =========================================================

    return {
        "organization_id": organization_id,

        "collaborations": {
            "total": collaboration_total,
            "draft": collaboration_draft,
            "submitted": collaboration_submitted,
            "under_review": collaboration_under_review,
            "accepted": collaboration_accepted,
            "rejected": collaboration_rejected,
        },

        "projects": {
            "total": project_total,
            "planning": project_planning,
            "active": project_active,
            "on_hold": project_on_hold,
            "completed": project_completed,
        },

        "milestones": {
            "total": milestone_total,
            "completed": milestone_completed,
            "delayed": milestone_delayed,
            "blocked": milestone_blocked,
        },

        "deliverables": {
            "total": deliverable_total,
            "approved": deliverable_approved,
            "rejected": deliverable_rejected,
        },

        "funding": {
            "allocated": round(allocated, 2),
            "disbursed": round(disbursed, 2),
            "utilized": round(utilized, 2),
            "refunded": round(refunded, 2),
        },

        "impact": {
            "verified_outcomes": verified_outcomes,
            "beneficiaries": int(beneficiaries),
            "average_project_progress": round(
                float(average_project_progress),
                2,
            ),
        },

        "reputation": {
            "total_points": reputation_points,
            "contribution_count": reputation_contributions,
        },
    }