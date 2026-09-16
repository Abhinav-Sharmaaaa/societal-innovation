from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User, UserRole


EMAIL = "university.admin@uiu.ac.in"
PASSWORD = "12345678"
FULL_NAME = "Uttarakhand Innovation University Admin"
ORGANIZATION_ID = 4


def main() -> None:
    db = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.email == EMAIL)
            .first()
        )

        if existing_user:
            print(f"User already exists: {existing_user.email}")
            print(f"Role: {existing_user.role}")
            print(f"Organization ID: {existing_user.organization_id}")
            return

        user = User(
            full_name=FULL_NAME,
            email=EMAIL,
            phone=None,
            password_hash=hash_password(PASSWORD),
            role=UserRole.UNIVERSITY_ADMIN,
            organization_id=ORGANIZATION_ID,
            is_active=True,
            is_verified=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("University admin created successfully.")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Organization ID: {user.organization_id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()