from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.dependencies import get_db
from app.models.challenge import Challenge
from app.models.challenge_evidence import ChallengeEvidence
from app.models.user import User

router = APIRouter(prefix="/sync", tags=["Sync"])

class SyncData(BaseModel):
    # Depending on what the PC backend needs, we can return users, challenges, etc.
    # For simplicity, returning raw dicts or customized Pydantic models.
    pass

@router.get("/pull/challenges")
def pull_challenges(db: Session = Depends(get_db)):
    # The PC backend calls this to pull new challenges submitted by mobile users
    challenges = db.query(Challenge).filter(Challenge.status == "SUBMITTED").all()
    # In a real app we'd mark them as "pulled" or "synced" but for now just return them
    result = []
    for c in challenges:
        try:
            # Get evidence
            evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == c.id).all()

            def _enum_value(v):
                return v.value if hasattr(v, "value") else v

            result.append({
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "submitted_by": c.submitted_by,
                "is_anonymous": c.is_anonymous,
                "upvotes": c.upvotes,

                # Classification -- previously dropped entirely, which is
                # why every mobile-synced report showed up on the web
                # dashboard with generic defaults (category OTHER,
                # severity/urgency MEDIUM) no matter what the AI triage
                # on this side had actually determined.
                "category": _enum_value(c.category),
                "severity": _enum_value(c.severity),
                "urgency": _enum_value(c.urgency),

                # Impact / location
                "affected_population": c.affected_population,
                "estimated_economic_loss": c.estimated_economic_loss,
                "address": c.address,
                "district": c.district,
                "state": c.state,
                "latitude": c.latitude,
                "longitude": c.longitude,

                # Location resolution
                "location_source": _enum_value(c.location_source),
                "location_verified": c.location_verified,
                "location_accuracy_meters": c.location_accuracy_meters,
                "locality": c.locality,
                "location_resolution_reason": c.location_resolution_reason,
                "location_resolved_at": c.location_resolved_at.isoformat() if c.location_resolved_at else None,

                # AI / innovation assessment
                "innovation_required": c.innovation_required,
                "ai_innovation_confidence": c.ai_innovation_confidence,
                "ai_innovation_decision": c.ai_innovation_decision,
                "ai_innovation_requires_human_review": c.ai_innovation_requires_human_review,
                "ai_innovation_type": c.ai_innovation_type,
                "ai_innovation_type_confidence": c.ai_innovation_type_confidence,
                "ai_innovation_type_second": c.ai_innovation_type_second,
                "ai_innovation_type_second_confidence": c.ai_innovation_type_second_confidence,
                "ai_innovation_type_margin": c.ai_innovation_type_margin,
                "ai_innovation_type_decision": c.ai_innovation_type_decision,
                "ai_innovation_type_requires_human_review": c.ai_innovation_type_requires_human_review,
                "ai_innovation_type_top_3": c.ai_innovation_type_top_3,
                "ai_confidence_score": c.ai_confidence_score,
                "ai_model_version": c.ai_model_version,
                "ai_category_confidence": c.ai_category_confidence,
                "ai_second_category": c.ai_second_category,
                "ai_second_category_confidence": c.ai_second_category_confidence,
                "ai_category_margin": c.ai_category_margin,
                "ai_category_decision": c.ai_category_decision,
                "ai_requires_human_review": c.ai_requires_human_review,
                "ai_category_top_3": c.ai_category_top_3,
                "ai_analysis_at": c.ai_analysis_at.isoformat() if c.ai_analysis_at else None,

                # Routing
                "routing_type": _enum_value(c.routing_type),
                "routing_reason": c.routing_reason,
                "current_authority_id": c.current_authority_id,
                "assigned_at": c.assigned_at.isoformat() if c.assigned_at else None,
                "assigned_by": c.assigned_by,

                # Lifecycle / duplicate detection
                "status": _enum_value(c.status),
                "is_master_challenge": c.is_master_challenge,
                "master_challenge_id": c.master_challenge_id,
                "duplicate_similarity_score": c.duplicate_similarity_score,

                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),

                "evidences": [
                    {"file_url": e.file_url, "type": e.evidence_type}
                    for e in evidences
                ],
            })
        except Exception as exc:
            # Don't let one malformed challenge/evidence row take down the
            # entire pull -- skip it and keep going so everything else still
            # syncs. It'll be retried on the next pull once whatever's wrong
            # with it is fixed.
            print(f"Skipping challenge {c.id} in pull_challenges: {exc}")
            continue
    return {"challenges": result}

@router.post("/push/challenges")
def push_challenge_status(updates: list[dict], db: Session = Depends(get_db)):
    # The PC backend pushes status updates (e.g. from SUBMITTED to RESOLVED)
    for update in updates:
        challenge = db.query(Challenge).filter(Challenge.id == update["id"]).first()
        if challenge:
            challenge.status = update.get("status", challenge.status)
            db.commit()
    return {"message": "Statuses updated"}