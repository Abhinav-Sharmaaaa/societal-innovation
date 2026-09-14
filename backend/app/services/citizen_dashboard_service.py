from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.challenge import (
    Challenge,
    ChallengeStatus,
)
from app.models.reputation_score import ReputationScore
from app.models.user import User


def get_citizen_dashboard(
    db: Session,
    current_user: User,
) -> dict:

    user_id = current_user.id

    # =========================================================
    # CHALLENGE COUNTS
    # =========================================================

    total = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id
        )
        .scalar()
        or 0
    )

    submitted = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.SUBMITTED,
        )
        .scalar()
        or 0
    )

    under_review = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.UNDER_REVIEW,
        )
        .scalar()
        or 0
    )

    routed = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.ROUTED,
        )
        .scalar()
        or 0
    )

    in_progress = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.IN_PROGRESS,
        )
        .scalar()
        or 0
    )

    resolved = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.RESOLVED,
        )
        .scalar()
        or 0
    )

    rejected = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.REJECTED,
        )
        .scalar()
        or 0
    )

    closed = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.status == ChallengeStatus.CLOSED,
        )
        .scalar()
        or 0
    )

    innovation_required = (
        db.query(func.count(Challenge.id))
        .filter(
            Challenge.submitted_by == user_id,
            Challenge.innovation_required.is_(True),
        )
        .scalar()
        or 0
    )

    # =========================================================
    # RECENT CHALLENGES
    # =========================================================

    recent_challenges = (
        db.query(Challenge)
        .filter(
            Challenge.submitted_by == user_id
        )
        .order_by(
            Challenge.created_at.desc()
        )
        .limit(10)
        .all()
    )

    recent_challenge_data = [
        {
            "id": challenge.id,
            "title": challenge.title,
            "status": (
                challenge.status.value
                if hasattr(challenge.status, "value")
                else str(challenge.status)
            ),
            "category": (
                challenge.category.value
                if hasattr(challenge.category, "value")
                else str(challenge.category)
            ),
            "urgency": (
                challenge.urgency.value
                if hasattr(challenge.urgency, "value")
                else str(challenge.urgency)
            ),
            "innovation_required": (
                challenge.innovation_required
            ),
            "district": challenge.district,
            "state": challenge.state,
            "current_authority_id": (
                challenge.current_authority_id
            ),
            "created_at": (
                challenge.created_at
            ),
            "updated_at": (
                challenge.updated_at
            ),
        }
        for challenge in recent_challenges
    ]

    # =========================================================
    # REPUTATION
    # =========================================================

    reputation = (
        db.query(ReputationScore)
        .filter(
            ReputationScore.user_id == user_id,
            ReputationScore.organization_id.is_(None),
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
        "user_id": user_id,

        "challenge_stats": {
            "total": total,
            "submitted": submitted,
            "under_review": under_review,
            "routed": routed,
            "in_progress": in_progress,
            "resolved": resolved,
            "rejected": rejected,
            "closed": closed,
            "innovation_required": innovation_required,
        },

        "reputation": {
            "total_points": reputation_points,
            "contribution_count": reputation_contributions,
        },

        "recent_challenges": recent_challenge_data,
    }