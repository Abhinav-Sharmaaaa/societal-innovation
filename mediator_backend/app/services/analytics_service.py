from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.challenge import (
    Challenge,
    ChallengeStatus,
    ChallengeCategory,
)
from app.models.organization import (
    Organization,
    OrganizationType,
)
from app.models.project import (
    Project,
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
from app.models.reputation_score import (
    ReputationScore,
    ReputationScoreEntityType,
)


# ============================================================
# OVERVIEW
# ============================================================

def get_analytics_overview(
    db: Session,
) -> dict:

    total_challenges = (
        db.query(func.count(Challenge.id))
        .scalar()
        or 0
    )

    resolved_challenges = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.status.in_(
                [
                    ChallengeStatus.RESOLVED,
                    ChallengeStatus.CLOSED,
                ]
            )
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

    total_projects = (
        db.query(func.count(Project.id))
        .scalar()
        or 0
    )

    active_projects = (
        db.query(func.count(Project.id))
        .filter(
            Project.status == ProjectStatus.ACTIVE
        )
        .scalar()
        or 0
    )

    completed_projects = (
        db.query(func.count(Project.id))
        .filter(
            Project.status
            == ProjectStatus.COMPLETED
        )
        .scalar()
        or 0
    )

    universities = (
        db.query(func.count(Organization.id))
        .filter(
            Organization.organization_type
            == OrganizationType.UNIVERSITY,
            Organization.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    industries = (
        db.query(func.count(Organization.id))
        .filter(
            Organization.organization_type
            == OrganizationType.INDUSTRY,
            Organization.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    verified_outcomes = (
        db.query(func.count(ProjectOutcome.id))
        .filter(
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED
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
        .filter(
            ProjectOutcome.status
            == ProjectOutcomeStatus.VERIFIED
        )
        .scalar()
        or 0
    )

    resolution_rate = (
        round(
            (
                resolved_challenges
                / total_challenges
            )
            * 100,
            2,
        )
        if total_challenges
        else 0
    )

    return {
        "challenges": {
            "total": total_challenges,
            "resolved": resolved_challenges,
            "innovation_required": innovation_challenges,
            "resolution_rate": resolution_rate,
        },
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "completed": completed_projects,
        },
        "ecosystem": {
            "universities": universities,
            "industries": industries,
        },
        "impact": {
            "verified_outcomes": verified_outcomes,
            "beneficiaries": int(beneficiaries),
        },
    }


# ============================================================
# DISTRICT ANALYTICS
# ============================================================

def get_district_analytics(
    db: Session,
) -> list[dict]:

    rows = (
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

    result = []

    for district, challenge_count in rows:

        resolved_count = (
            db.query(func.count(Challenge.id))
            .filter(
                Challenge.district == district,
                Challenge.status.in_(
                    [
                        ChallengeStatus.RESOLVED,
                        ChallengeStatus.CLOSED,
                    ]
                ),
            )
            .scalar()
            or 0
        )

        innovation_count = (
            db.query(func.count(Challenge.id))
            .filter(
                Challenge.district == district,
                Challenge.innovation_required.is_(True),
            )
            .scalar()
            or 0
        )

        result.append(
            {
                "district": district,
                "challenge_count": challenge_count,
                "resolved_count": resolved_count,
                "innovation_count": innovation_count,
            }
        )

    return result


# ============================================================
# UNIVERSITY LEADERBOARD
# ============================================================

def get_university_leaderboard(
    db: Session,
) -> list[dict]:

    universities = (
        db.query(Organization)
        .filter(
            Organization.organization_type
            == OrganizationType.UNIVERSITY,
            Organization.is_active.is_(True),
        )
        .all()
    )

    result = []

    for university in universities:

        reputation = (
            db.query(ReputationScore)
            .filter(
                ReputationScore.organization_id
                == university.id,
                ReputationScore.entity_type
                == ReputationScoreEntityType.UNIVERSITY,
            )
            .first()
        )

        project_count = (
            db.query(func.count(Project.id))
            .filter(
                Project.university_id
                == university.id
            )
            .scalar()
            or 0
        )

        completed_projects = (
            db.query(func.count(Project.id))
            .filter(
                Project.university_id
                == university.id,
                Project.status
                == ProjectStatus.COMPLETED,
            )
            .scalar()
            or 0
        )

        verified_outcomes = (
            db.query(func.count(ProjectOutcome.id))
            .join(
                Project,
                ProjectOutcome.project_id
                == Project.id,
            )
            .filter(
                Project.university_id
                == university.id,
                ProjectOutcome.status
                == ProjectOutcomeStatus.VERIFIED,
            )
            .scalar()
            or 0
        )

        result.append(
            {
                "organization_id": university.id,
                "organization_name": university.name,
                "reputation_points": (
                    reputation.total_points
                    if reputation
                    else 0
                ),
                "projects": project_count,
                "completed_projects": completed_projects,
                "verified_outcomes": verified_outcomes,
            }
        )

    result.sort(
        key=lambda item: (
            item["reputation_points"],
            item["completed_projects"],
            item["verified_outcomes"],
        ),
        reverse=True,
    )

    return result


# ============================================================
# INDUSTRY LEADERBOARD
# ============================================================

def get_industry_leaderboard(
    db: Session,
) -> list[dict]:

    industries = (
        db.query(Organization)
        .filter(
            Organization.organization_type
            == OrganizationType.INDUSTRY,
            Organization.is_active.is_(True),
        )
        .all()
    )

    result = []

    for industry in industries:

        reputation = (
            db.query(ReputationScore)
            .filter(
                ReputationScore.organization_id
                == industry.id,
                ReputationScore.entity_type
                == ReputationScoreEntityType.INDUSTRY,
            )
            .first()
        )

        project_count = (
            db.query(func.count(Project.id))
            .filter(
                Project.industry_id
                == industry.id
            )
            .scalar()
            or 0
        )

        completed_projects = (
            db.query(func.count(Project.id))
            .filter(
                Project.industry_id
                == industry.id,
                Project.status
                == ProjectStatus.COMPLETED,
            )
            .scalar()
            or 0
        )

        funding_transactions = (
            db.query(ProjectFundingTransaction)
            .join(
                Project,
                ProjectFundingTransaction.project_id
                == Project.id,
            )
            .filter(
                Project.industry_id
                == industry.id,
                ProjectFundingTransaction.status
                == FundingTransactionStatus.COMPLETED,
            )
            .all()
        )

        total_funding = 0.0

        for transaction in funding_transactions:

            if transaction.transaction_type in {
                FundingTransactionType.ALLOCATION,
                FundingTransactionType.DISBURSEMENT,
            }:
                total_funding += float(
                    transaction.amount or 0
                )

        result.append(
            {
                "organization_id": industry.id,
                "organization_name": industry.name,
                "reputation_points": (
                    reputation.total_points
                    if reputation
                    else 0
                ),
                "projects": project_count,
                "completed_projects": completed_projects,
                "funding_contribution": round(
                    total_funding,
                    2,
                ),
            }
        )

    result.sort(
        key=lambda item: (
            item["reputation_points"],
            item["funding_contribution"],
            item["completed_projects"],
        ),
        reverse=True,
    )

    return result


# ============================================================
# REPUTATION LEADERBOARD
# ============================================================

def get_reputation_leaderboard(
    db: Session,
    entity_type: ReputationScoreEntityType | None = None,
) -> list[dict]:

    query = db.query(ReputationScore)

    if entity_type is not None:
        query = query.filter(
            ReputationScore.entity_type
            == entity_type
        )

    scores = (
        query
        .order_by(
            ReputationScore.total_points.desc()
        )
        .all()
    )

    result = []

    for score in scores:

        organization_name = None

        if score.organization_id is not None:

            organization = (
                db.query(Organization)
                .filter(
                    Organization.id
                    == score.organization_id
                )
                .first()
            )

            if organization:
                organization_name = (
                    organization.name
                )

        result.append(
            {
                "entity_type": (
                    score.entity_type.value
                ),
                "organization_id": score.organization_id,
                "organization_name": organization_name,
                "total_points": score.total_points,
                "contribution_count": (
                    score.contribution_count
                ),
            }
        )

    return result