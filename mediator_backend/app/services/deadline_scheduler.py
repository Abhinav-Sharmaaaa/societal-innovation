from app.db.database import SessionLocal
from app.services.deadline_service import run_deadline_scan


def scheduled_deadline_scan() -> None:
    db = SessionLocal()

    try:
        run_deadline_scan(db)

    except Exception:
        db.rollback()

    finally:
        db.close()