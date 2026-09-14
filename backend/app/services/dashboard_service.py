from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.challenge import (
    Challenge,
    ChallengeStatus,
    ChallengeUrgency,
)
from app.models.organization import (
    Organization,
    OrganizationType,
)
from app.models.project import (
    Project,
    ProjectHealth,
    ProjectStatus,
)
from app.models.project_funding import (
    FundingTransactionStatus,
    FundingTransactionType,
    ProjectFundingTransaction,
)
from app.models.project_outcome import (
    ProjectOutcome,
    ProjectOutcomeStatus,
)


def get_government_dashboard(
    db: Session,
) -> dict:
    """
    Returns aggregated platform statistics for the
    government dashboard.

    This service is intentionally read-only.
    No data is modified here.
    """

    # =========================================================
    # CHALLENGE STATISTICS
    # =========================================================

    challenge_total = (
        db.query(func.count(Challenge.id))
        .scalar()
        or 0
    )

    challenge_submitted = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.SUBMITTED
        )
        .scalar()
        or 0
    )

    challenge_under_review = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.UNDER_REVIEW
        )
        .scalar()
        or 0
    )

    challenge_routed = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.ROUTED
        )
        .scalar()
        or 0
    )

    challenge_in_progress = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.IN_PROGRESS
        )
        .scalar()
        or 0
    )

    challenge_resolved = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.RESOLVED
        )
        .scalar()
        or 0
    )

    challenge_rejected = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.REJECTED
        )
        .scalar()
        or 0
    )

    challenge_closed = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status
            == ChallengeStatus.CLOSED
        )
        .scalar()
        or 0
    )

    innovation_challenges = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.innovation_required.is_(True)
        )
        .scalar()
        or 0
    )

    high_priority_challenges = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.urgency.in_(
                [
                    ChallengeUrgency.HIGH,
                    ChallengeUrgency.CRITICAL,
                ]
            )
        )
        .scalar()
        or 0
    )

    # =========================================================
    # PROJECT STATISTICS
    # =========================================================

    project_total = (
        db.query(func.count(Project.id))
        .scalar()
        or 0
    )

    project_planning = (
        db.query(func.count(Project.id))
        .filter(
            Project.status
            == ProjectStatus.PLANNING
        )
        .scalar()
        or 0
    )

    project_active = (
        db.query(func.count(Project.id))
        .filter(
            Project.status
            == ProjectStatus.ACTIVE
        )
        .scalar()
        or 0
    )

    project_on_hold = (
        db.query(func.count(Project.id))
        .filter(
            Project.status
            == ProjectStatus.ON_HOLD
        )
        .scalar()
        or 0
    )

    project_completed = (
        db.query(func.count(Project.id))
        .filter(
            Project.status
            == ProjectStatus.COMPLETED
        )
        .scalar()
        or 0
    )

    project_cancelled = (
        db.query(func.count(Project.id))
        .filter(
            Project.status
            == ProjectStatus.CANCELLED
        )
        .scalar()
        or 0
    )

    # =========================================================
    # PROJECT HEALTH
    # =========================================================

    projects_on_track = (
        db.query(func.count(Project.id))
        .filter(
            Project.health
            == ProjectHealth.ON_TRACK
        )
        .scalar()
        or 0
    )

    projects_at_risk = (
        db.query(func.count(Project.id))
        .filter(
            Project.health
            == ProjectHealth.AT_RISK
        )
        .scalar()
        or 0
    )

    projects_delayed = (
        db.query(func.count(Project.id))
        .filter(
            Project.health
            == ProjectHealth.DELAYED
        )
        .scalar()
        or 0
    )

    projects_critical = (
        db.query(func.count(Project.id))
        .filter(
            Project.health
            == ProjectHealth.CRITICAL
        )
        .scalar()
        or 0
    )

    # =========================================================
    # ECOSYSTEM COUNTS
    # =========================================================

    university_count = (
        db.query(func.count(Organization.id))
        .filter(
            Organization.organization_type
            == OrganizationType.UNIVERSITY,
            Organization.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    industry_count = (
        db.query(func.count(Organization.id))
        .filter(
            Organization.organization_type
            == OrganizationType.INDUSTRY,
            Organization.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    # =========================================================
    # FUNDING
    # =========================================================
    #
    # Only COMPLETED transactions are included because
    # the funding summary in the project workflow uses
    # completed financial transactions.
    # =========================================================

    completed_funding = (
        db.query(ProjectFundingTransaction)
        .filter(
            ProjectFundingTransaction.status
            == FundingTransactionStatus.COMPLETED
        )
        .all()
    )

    allocated = 0.0
    disbursed = 0.0
    utilized = 0.0
    refunded = 0.0

    for transaction in completed_funding:

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

    remaining = max(
        allocated - disbursed + refunded,
        0,
    )

    # =========================================================
    # OUTCOME / IMPACT STATISTICS
    # =========================================================

    verified_outcomes = (
        db.query(func.count(ProjectOutcome.id))
        .filter(
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED
        )
        .scalar()
        or 0
    )

    total_beneficiaries = (
        db.query(
            func.coalesce(
                func.sum(
                    ProjectOutcome.beneficiary_count
                ),
                0,
            )
        )
        .filter(
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED
        )
        .scalar()
        or 0
    )

    # =========================================================
    # AVERAGE PROJECT PROGRESS
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
        .scalar()
        or 0
    )

    # =========================================================
    # CHALLENGE CATEGORY DISTRIBUTION
    # =========================================================

    category_rows = (
        db.query(
            Challenge.category,
            func.count(Challenge.id),
        )
        .group_by(
            Challenge.category
        )
        .all()
    )

    category_distribution = {
        (
            category.value
            if hasattr(category, "value")
            else str(category)
        ): count
        for category, count in category_rows
    }

    # =========================================================
    # CHALLENGE DISTRICT DISTRIBUTION
    # =========================================================

    district_rows = (
        db.query(
            Challenge.district,
            func.count(Challenge.id),
        )
        .filter(
            Challenge.district.isnot(None),
            Challenge.district != "",
        )
        .group_by(
            Challenge.district
        )
        .order_by(
            func.count(Challenge.id).desc()
        )
        .all()
    )

    district_distribution = [
        {
            "district": district,
            "challenge_count": count,
        }
        for district, count in district_rows
    ]

    # =========================================================
    # FINAL RESPONSE
    # =========================================================

    return {
        "challenge_stats": {
            "total": challenge_total,
            "submitted": challenge_submitted,
            "under_review": challenge_under_review,
            "routed": challenge_routed,
            "in_progress": challenge_in_progress,
            "resolved": challenge_resolved,
            "rejected": challenge_rejected,
            "closed": challenge_closed,
            "innovation_required": innovation_challenges,
            "high_priority": high_priority_challenges,
        },

        "project_stats": {
            "total": project_total,
            "planning": project_planning,
            "active": project_active,
            "on_hold": project_on_hold,
            "completed": project_completed,
            "cancelled": project_cancelled,
        },

        "project_health": {
            "on_track": projects_on_track,
            "at_risk": projects_at_risk,
            "delayed": projects_delayed,
            "critical": projects_critical,
        },

        "ecosystem": {
            "universities": university_count,
            "industries": industry_count,
        },

        "funding": {
            "allocated": round(allocated, 2),
            "disbursed": round(disbursed, 2),
            "utilized": round(utilized, 2),
            "refunded": round(refunded, 2),
            "remaining": round(remaining, 2),
        },

        "impact": {
            "verified_outcomes": verified_outcomes,
            "total_beneficiaries": int(
                total_beneficiaries
            ),
            "average_project_progress": round(
                float(average_project_progress),
                2,
            ),
        },

        "distribution": {
            "challenge_categories": category_distribution,
            "challenge_districts": district_distribution,
        },
    }