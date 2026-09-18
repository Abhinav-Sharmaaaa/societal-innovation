import os
import requests
from app.db.database import SessionLocal
from app.models.challenge import Challenge
from app.models.user import User


def _mediator_url() -> str:
    """Read MEDIATOR_URL at call time so dotenv is guaranteed to be loaded."""
    return os.environ.get(
        "MEDIATOR_URL",
        "https://societal-innovation-ieeu.onrender.com/api/v1",
    )


def pull_challenges():
    url = _mediator_url()
    print(f"Pulling challenges from {url}/sync/pull/challenges...")
    try:
        response = requests.get(f"{url}/sync/pull/challenges", timeout=30)
        if response.status_code == 200:
            data = response.json()
            challenges = data.get("challenges", [])
            print(f"Found {len(challenges)} new challenges.")
            db = SessionLocal()
            try:
                for c_data in challenges:
                    existing = db.query(Challenge).filter(Challenge.id == c_data["id"]).first()
                    if existing:
                        continue
                    print(f"Importing challenge {c_data['id']}: {c_data['title']}")
                    # Pull the full field set from the mediator response --
                    # previously only 9 basic fields were used, so every
                    # mobile-synced report lost its real classification
                    # (severity/urgency/district/AI fields) and fell back
                    # to this model's generic defaults on import.
                    new_c = Challenge(
                        id=c_data["id"],
                        title=c_data["title"],
                        description=c_data["description"],
                        submitted_by=c_data["submitted_by"],
                        is_anonymous=c_data.get("is_anonymous", False),
                        upvotes=c_data.get("upvotes", 0),

                        category=c_data.get("category", "OTHER"),
                        severity=c_data.get("severity", "MEDIUM"),
                        urgency=c_data.get("urgency", "MEDIUM"),

                        affected_population=c_data.get("affected_population"),
                        estimated_economic_loss=c_data.get("estimated_economic_loss"),
                        address=c_data.get("address"),
                        district=c_data.get("district"),
                        state=c_data.get("state"),
                        latitude=c_data.get("latitude"),
                        longitude=c_data.get("longitude"),

                        location_source=c_data.get("location_source", "MANUAL"),
                        location_verified=c_data.get("location_verified", False),
                        location_accuracy_meters=c_data.get("location_accuracy_meters"),
                        locality=c_data.get("locality"),
                        location_resolution_reason=c_data.get("location_resolution_reason"),

                        innovation_required=c_data.get("innovation_required", False),
                        ai_innovation_confidence=c_data.get("ai_innovation_confidence"),
                        ai_innovation_decision=c_data.get("ai_innovation_decision"),
                        ai_innovation_requires_human_review=c_data.get("ai_innovation_requires_human_review"),
                        ai_innovation_type=c_data.get("ai_innovation_type"),
                        ai_innovation_type_confidence=c_data.get("ai_innovation_type_confidence"),
                        ai_innovation_type_second=c_data.get("ai_innovation_type_second"),
                        ai_innovation_type_second_confidence=c_data.get("ai_innovation_type_second_confidence"),
                        ai_innovation_type_margin=c_data.get("ai_innovation_type_margin"),
                        ai_innovation_type_decision=c_data.get("ai_innovation_type_decision"),
                        ai_innovation_type_requires_human_review=c_data.get("ai_innovation_type_requires_human_review"),
                        ai_innovation_type_top_3=c_data.get("ai_innovation_type_top_3"),
                        ai_confidence_score=c_data.get("ai_confidence_score"),
                        ai_model_version=c_data.get("ai_model_version"),
                        ai_category_confidence=c_data.get("ai_category_confidence"),
                        ai_second_category=c_data.get("ai_second_category"),
                        ai_second_category_confidence=c_data.get("ai_second_category_confidence"),
                        ai_category_margin=c_data.get("ai_category_margin"),
                        ai_category_decision=c_data.get("ai_category_decision"),
                        ai_requires_human_review=c_data.get("ai_requires_human_review"),
                        ai_category_top_3=c_data.get("ai_category_top_3"),

                        routing_type=c_data.get("routing_type", "HUMAN_REVIEW"),
                        routing_reason=c_data.get("routing_reason"),
                        current_authority_id=c_data.get("current_authority_id"),
                        assigned_by=c_data.get("assigned_by"),

                        status=c_data["status"],
                        is_master_challenge=c_data.get("is_master_challenge", False),
                        master_challenge_id=c_data.get("master_challenge_id"),
                        duplicate_similarity_score=c_data.get("duplicate_similarity_score"),
                    )
                    db.add(new_c)
                db.commit()
            finally:
                db.close()
        else:
            print("Failed to pull challenges.", response.status_code)
    except Exception as e:
        print("Error pulling challenges:", e)


def push_statuses():
    url = _mediator_url()
    print(f"Pushing statuses to {url}/sync/push/challenges...")
    try:
        db = SessionLocal()
        try:
            challenges = db.query(Challenge).filter(Challenge.status != "SUBMITTED").all()
            updates = [
                {
                    "id": c.id,
                    "status": c.status.value if hasattr(c.status, "value") else c.status,
                }
                for c in challenges
            ]
            if updates:
                response = requests.post(
                    f"{url}/sync/push/challenges",
                    json=updates,
                    timeout=30,
                )
                print("Push result:", response.status_code)
            else:
                print("No status updates to push.")
        finally:
            db.close()
    except Exception as e:
        print("Error pushing statuses:", e)


def perform_sync():
    pull_challenges()
    push_statuses()