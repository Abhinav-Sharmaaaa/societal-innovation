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
                    if not existing:
                        print(f"Importing challenge {c_data['id']}: {c_data['title']}")
                        new_c = Challenge(
                            id=c_data["id"],
                            title=c_data["title"],
                            description=c_data["description"],
                            category=c_data["category"],
                            latitude=c_data.get("latitude"),
                            longitude=c_data.get("longitude"),
                            is_anonymous=c_data.get("is_anonymous", False),
                            upvotes=c_data.get("upvotes", 0),
                            submitted_by=c_data["submitted_by"],
                            status=c_data["status"],
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
