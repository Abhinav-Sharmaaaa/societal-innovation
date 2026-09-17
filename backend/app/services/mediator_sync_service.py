import os
import requests
import time
from app.db.database import SessionLocal
from app.models.challenge import Challenge
from app.models.user import User

MEDIATOR_URL = os.environ.get("MEDIATOR_URL", "http://localhost:8001/api/v1")

def pull_challenges():
    print(f"Pulling challenges from {MEDIATOR_URL}/sync/pull/challenges...")
    try:
        response = requests.get(f"{MEDIATOR_URL}/sync/pull/challenges")
        if response.status_code == 200:
            data = response.json()
            challenges = data.get("challenges", [])
            print(f"Found {len(challenges)} new challenges.")
            db = SessionLocal()
            try:
                for c_data in challenges:
                    # check if already exists
                    existing = db.query(Challenge).filter(Challenge.id == c_data["id"]).first()
                    if not existing:
                        print(f"Importing challenge {c_data['id']}: {c_data['title']}")
                        new_c = Challenge(
                            id=c_data["id"],
                            title=c_data["title"],
                            description=c_data["description"],
                            category=c_data["category"],
                            latitude=c_data["latitude"],
                            longitude=c_data["longitude"],
                            is_anonymous=c_data["is_anonymous"],
                            upvotes=c_data["upvotes"],
                            submitted_by=c_data["submitted_by"],
                            status=c_data["status"]
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
    print(f"Pushing statuses to {MEDIATOR_URL}/sync/push/challenges...")
    try:
        db = SessionLocal()
        try:
            # find challenges that have been resolved or are not SUBMITTED
            challenges = db.query(Challenge).filter(Challenge.status != "SUBMITTED").all()
            updates = [{"id": c.id, "status": c.status.value if hasattr(c.status, "value") else c.status} for c in challenges]
            if updates:
                response = requests.post(f"{MEDIATOR_URL}/sync/push/challenges", json=updates)
                print("Push result:", response.status_code)
        finally:
            db.close()
    except Exception as e:
        print("Error pushing statuses:", e)


def perform_sync():
    pull_challenges()
    push_statuses()
