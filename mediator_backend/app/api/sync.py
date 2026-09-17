from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db
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
        # Get evidence
        evidences = db.query(ChallengeEvidence).filter(ChallengeEvidence.challenge_id == c.id).all()
        result.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "submitted_by": c.submitted_by,
            "category": c.category,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "is_anonymous": c.is_anonymous,
            "upvotes": c.upvotes,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "evidences": [{"file_path": e.file_path, "type": e.type} for e in evidences]
        })
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
