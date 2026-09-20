from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import (
    Challenge,
    ChallengeLocationSource,
    ChallengeStatus,
)
from app.models.user import User
from app.schemas.challenge import ChallengeCreate, ChallengeUpdate
from app.ai.schemas import TriageRequest
from app.ai.triage_service import triage_challenge
from app.models.challenge_evidence import ChallengeEvidence, EvidenceType
import json


# ============================================================
# Create Challenge
# ============================================================

def create_challenge(
    db: Session,
    challenge_data: ChallengeCreate,
    current_user: User,
) -> Challenge:

    location_resolved_at = None

    if challenge_data.location_source in {
        ChallengeLocationSource.GPS,
        ChallengeLocationSource.GPS_VERIFIED_MANUAL,
        ChallengeLocationSource.CONFLICT,
    }:
        location_resolved_at = datetime.now(timezone.utc)

    challenge = Challenge(
        # ----------------------------------------------------
        # Basic Information
        # ----------------------------------------------------

        title=challenge_data.title,
        description=challenge_data.description,
        submitted_by=current_user.id,

        # ----------------------------------------------------
        # Initial Classification
        # ----------------------------------------------------

        category=challenge_data.category,
        urgency=challenge_data.urgency,

        # ----------------------------------------------------
        # Impact
        # ----------------------------------------------------

        affected_population=challenge_data.affected_population,
        estimated_economic_loss=(
            challenge_data.estimated_economic_loss
        ),

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        address=challenge_data.address,
        district=challenge_data.district,
        state=challenge_data.state,
        locality=challenge_data.locality,

        latitude=challenge_data.latitude,
        longitude=challenge_data.longitude,

        # ----------------------------------------------------
        # Location Resolution Metadata
        # ----------------------------------------------------

        location_source=challenge_data.location_source,
        location_verified=challenge_data.location_verified,
        location_accuracy_meters=(
            challenge_data.location_accuracy_meters
        ),
        location_resolution_reason=(
            challenge_data.location_resolution_reason
        ),
        location_resolved_at=location_resolved_at,
    )

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    if challenge_data.media_ids:
        for media_id_str in challenge_data.media_ids:
            try:
                metadata = json.loads(media_id_str)
                evidence = ChallengeEvidence(
                    challenge_id=challenge.id,
                    evidence_type=EvidenceType(metadata["evidence_type"]),
                    original_filename=metadata["original_filename"],
                    stored_filename=metadata["stored_filename"],
                    content_type=metadata["content_type"],
                    file_size=metadata["file_size"],
                    file_url=metadata["file_url"],
                    uploaded_by=current_user.id
                )
                db.add(evidence)
            except Exception as e:
                # Log error or continue
                print(f"Failed to process media_id {media_id_str}: {e}")
        db.commit()

    return challenge


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

    challenge = db.scalar(statement)
    
    if challenge:
        _ensure_ai_analysis(db, [challenge])
        
    return challenge


# ============================================================
# Dynamic AI Analysis Helper
# ============================================================

def _ensure_ai_analysis(db: Session, challenges: list[Challenge]):
    for challenge in challenges:
        if challenge.ai_analysis_at is None:
            # Construct a request for the local AI models
            request = TriageRequest(
                title=challenge.title,
                description=challenge.description,
                category=challenge.category,
                address=challenge.address,
                district=challenge.district,
                state=challenge.state,
                affected_population=challenge.affected_population,
                estimated_economic_loss=challenge.estimated_economic_loss,
            )
            # Run triage locally
            triage_result = triage_challenge(request)
            # Persist it
            persist_ai_triage_result(db, challenge, triage_result)


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
        .order_by(Challenge.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    challenges = list(db.scalars(statement).all())
    _ensure_ai_analysis(db, challenges)
    return challenges


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
        .order_by(
            Challenge.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
    )

    challenges = list(db.scalars(statement).all())
    _ensure_ai_analysis(db, challenges)
    return challenges


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
    """
    Convert Pydantic models and nested structures into
    JSON-serializable Python primitives.
    """

    if value is None:
        return None

    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "dict"):
        return value.dict()

    if isinstance(value, list):
        return [
            _json_safe(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _json_safe(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: _json_safe(val)
            for key, val in value.items()
        }

    return value


# ============================================================
# Persist AI Triage Result
# ============================================================

def persist_ai_triage_result(
    db: Session,
    challenge: Challenge,
    triage_result,
) -> Challenge:
    """
    Persist the complete AI triage result.

    Category, severity, urgency, innovation, routing,
    model evidence, confidence values, and explanations
    are persisted for auditability and frontend display.
    """

    # ========================================================
    # CANONICAL TRIAGE VALUES
    # ========================================================

    challenge.category = (
        triage_result.category
    )

    challenge.severity = (
        triage_result.severity
    )

    challenge.urgency = (
        triage_result.urgency
    )

    challenge.innovation_required = (
        triage_result.innovation_required
    )

    # ========================================================
    # MODEL VERSION / GENERAL AI CONFIDENCE
    # ========================================================

    challenge.ai_confidence_score = (
        triage_result.category_confidence
    )

    challenge.ai_model_version = (
        triage_result.model_version
    )

    # ========================================================
    # CATEGORY AI EVIDENCE
    # ========================================================

    challenge.ai_category_confidence = (
        triage_result.category_confidence
    )

    challenge.ai_second_category = (
        triage_result.second_category
    )

    challenge.ai_second_category_confidence = (
        triage_result.second_category_confidence
    )

    challenge.ai_category_margin = (
        triage_result.category_margin
    )

    challenge.ai_category_decision = (
        triage_result.category_decision
    )

    challenge.ai_requires_human_review = (
        triage_result.requires_human_review
    )

    challenge.ai_category_top_3 = _json_safe(
        triage_result.category_top_3
    )

    # ========================================================
    # INNOVATION REQUIRED AI EVIDENCE
    # ========================================================

    challenge.ai_innovation_confidence = (
        triage_result.innovation_confidence
    )

    challenge.ai_innovation_decision = (
        triage_result.innovation_decision
    )

    challenge.ai_innovation_requires_human_review = (
        triage_result.innovation_requires_human_review
    )

    # ========================================================
    # INNOVATION TYPE AI EVIDENCE
    # ========================================================

    challenge.ai_innovation_type = (
        triage_result.innovation_type
    )

    challenge.ai_innovation_type_confidence = (
        triage_result.innovation_type_confidence
    )

    challenge.ai_innovation_type_second = (
        triage_result.innovation_type_second
    )

    challenge.ai_innovation_type_second_confidence = (
        triage_result.innovation_type_second_confidence
    )

    challenge.ai_innovation_type_margin = (
        triage_result.innovation_type_margin
    )

    challenge.ai_innovation_type_decision = (
        triage_result.innovation_type_decision
    )

    challenge.ai_innovation_type_requires_human_review = (
        triage_result.innovation_type_requires_human_review
    )

    challenge.ai_innovation_type_top_3 = _json_safe(
        triage_result.innovation_type_top_3
    )

    # ========================================================
    # ANALYSIS TIMESTAMP
    # ========================================================

    challenge.ai_analysis_at = (
        datetime.now(timezone.utc)
    )

    # ========================================================
    # ROUTING
    # ========================================================

    challenge.routing_type = (
        triage_result.routing_type
    )

    challenge.routing_reason = (
        triage_result.routing_reason
    )

    # ========================================================
    # FINAL CHALLENGE STATUS
    # ========================================================

    if triage_result.requires_human_review:
        challenge.status = (
            ChallengeStatus.UNDER_REVIEW
        )
    else:
        challenge.status = (
            ChallengeStatus.ROUTED
        )

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return challenge