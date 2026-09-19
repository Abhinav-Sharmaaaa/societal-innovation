from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.challenge import (
    Challenge,
    ChallengeLocationSource,
    ChallengeStatus,
)
from app.models.user import User
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate


# ============================================================
# Create Challenge
# ============================================================

def create_challenge(
    db: Session,
    challenge_data: ChallengeCreate,
    current_user: User,
    idempotency_key: str | None = None,
) -> Challenge:

    location_resolved_at = None

    if challenge_data.location_source in {
        ChallengeLocationSource.GPS,
        ChallengeLocationSource.GPS_VERIFIED_MANUAL,
        ChallengeLocationSource.CONFLICT,
    }:
        location_resolved_at = datetime.now(timezone.utc)

    challenge = Challenge(
        title=challenge_data.title,
        description=challenge_data.description,
        submitted_by=current_user.id,
        category=challenge_data.category,
        urgency=challenge_data.urgency,
        affected_population=challenge_data.affected_population,
        estimated_economic_loss=(
            challenge_data.estimated_economic_loss
        ),
        address=challenge_data.address,
        district=challenge_data.district,
        state=challenge_data.state,
        locality=challenge_data.locality,
        latitude=challenge_data.latitude,
        longitude=challenge_data.longitude,
        location_source=challenge_data.location_source,
        location_verified=challenge_data.location_verified,
        location_accuracy_meters=(
            challenge_data.location_accuracy_meters
        ),
        location_resolution_reason=(
            challenge_data.location_resolution_reason
        ),
        location_resolved_at=location_resolved_at,
        # Set atomically at construction time — no crash window between
        # insert and key-assignment that could cause a duplicate on retry.
        idempotency_key=idempotency_key,
    )

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return challenge


# ============================================================
# Get Challenge by Idempotency Key (for dedup on retry)
# ============================================================

def get_challenge_by_idempotency_key(
    db: Session,
    user_id: int,
    idempotency_key: str,
) -> Challenge | None:
    statement = select(Challenge).where(
        Challenge.submitted_by == user_id,
        Challenge.idempotency_key == idempotency_key,
    )
    return db.scalar(statement)


# ============================================================
# Get Challenge
# ============================================================

def get_challenge_by_id(
    db: Session,
    challenge_id: int,
) -> Challenge | None:
    statement = select(Challenge).where(
        Challenge.id == challenge_id
    )
    return db.scalar(statement)


# ============================================================
# Get Challenges
# ============================================================

def get_challenges(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[Challenge]:

    statement = (
        select(Challenge)
        .options(selectinload(Challenge.evidence))
        .order_by(Challenge.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).unique().all()
    )


# ============================================================
# Get User Challenges
# ============================================================

def get_user_challenges(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
) -> list[Challenge]:

    statement = (
        select(Challenge)
        .where(
            Challenge.submitted_by == user_id
        )
        .options(selectinload(Challenge.evidence))
        .order_by(
            Challenge.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.scalars(statement).unique().all()
    )


# ============================================================
# Update Challenge
# ============================================================

def update_challenge(
    db: Session,
    challenge: Challenge,
    challenge_data: ChallengeUpdate,
) -> Challenge:

    update_data = challenge_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            challenge,
            field,
            value,
        )

    db.commit()
    db.refresh(challenge)

    return challenge


# ============================================================
# JSON Safety Helper
# ============================================================

def _json_safe(value: Any):
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    return value


# ============================================================
# Persist AI Triage Result
# ============================================================

def persist_ai_triage_result(
    db: Session,
    challenge: Challenge,
    triage_result,
) -> Challenge:

    challenge.category = triage_result.category
    challenge.severity = triage_result.severity
    challenge.urgency = triage_result.urgency
    challenge.innovation_required = triage_result.innovation_required
    challenge.ai_confidence_score = triage_result.category_confidence
    challenge.ai_model_version = triage_result.model_version
    challenge.ai_category_confidence = triage_result.category_confidence
    challenge.ai_second_category = triage_result.second_category
    challenge.ai_second_category_confidence = triage_result.second_category_confidence
    challenge.ai_category_margin = triage_result.category_margin
    challenge.ai_category_decision = triage_result.category_decision
    challenge.ai_requires_human_review = triage_result.requires_human_review
    challenge.ai_category_top_3 = _json_safe(triage_result.category_top_3)
    challenge.ai_innovation_confidence = triage_result.innovation_confidence
    challenge.ai_innovation_decision = triage_result.innovation_decision
    challenge.ai_innovation_requires_human_review = triage_result.innovation_requires_human_review
    challenge.ai_innovation_type = triage_result.innovation_type
    challenge.ai_innovation_type_confidence = triage_result.innovation_type_confidence
    challenge.ai_innovation_type_second = triage_result.innovation_type_second
    challenge.ai_innovation_type_second_confidence = triage_result.innovation_type_second_confidence
    challenge.ai_innovation_type_margin = triage_result.innovation_type_margin
    challenge.ai_innovation_type_decision = triage_result.innovation_type_decision
    challenge.ai_innovation_type_requires_human_review = triage_result.innovation_type_requires_human_review
    challenge.ai_innovation_type_top_3 = _json_safe(triage_result.innovation_type_top_3)
    challenge.ai_analysis_at = datetime.now(timezone.utc)
    challenge.routing_type = triage_result.routing_type
    challenge.routing_reason = triage_result.routing_reason

    if triage_result.requires_human_review:
        challenge.status = ChallengeStatus.UNDER_REVIEW
    else:
        challenge.status = ChallengeStatus.ROUTED

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return challenge