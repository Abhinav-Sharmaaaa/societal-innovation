from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister


# ============================================================
# Find User By Email
# ============================================================

def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    """
    Retrieve a user using their email address.
    """

    statement = select(User).where(
        User.email == email
    )

    return db.scalar(statement)


# ============================================================
# Find User By Phone
# ============================================================

def get_user_by_phone(
    db: Session,
    phone: str,
) -> User | None:
    """
    Retrieve a user using their phone number.
    """

    statement = select(User).where(
        User.phone == phone
    )

    return db.scalar(statement)


# ============================================================
# Create User
# ============================================================

def create_user(
    db: Session,
    user_data: UserRegister,
) -> User:
    """
    Create a new citizen account.

    Public registration is restricted to CITIZEN accounts.
    """

    # --------------------------------------------------------
    # Normalize email
    # --------------------------------------------------------

    email = user_data.email.strip().lower()

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    existing_user = get_user_by_email(
        db=db,
        email=email,
    )

    if existing_user:
        raise ValueError(
            "A user with this email already exists."
        )

    # --------------------------------------------------------
    # Check duplicate phone
    # --------------------------------------------------------

    if user_data.phone:

        phone = user_data.phone.strip()

        existing_phone = get_user_by_phone(
            db=db,
            phone=phone,
        )

        if existing_phone:
            raise ValueError(
                "A user with this phone number already exists."
            )

    else:
        phone = None

    # --------------------------------------------------------
    # Security: public registration
    # --------------------------------------------------------

    if user_data.role != UserRole.CITIZEN:
        raise ValueError(
            "Public registration is only available for "
            "CITIZEN accounts."
        )

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    password_hash = hash_password(
        user_data.password
    )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    user = User(
        full_name=user_data.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        role=UserRole.CITIZEN,
        is_active=True,
        is_verified=False,
    )

    db.add(user)

    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        raise ValueError(
            "A user with the provided email or phone "
            "already exists."
        )

    db.refresh(user)

    return user


# ============================================================
# Authenticate User
# ============================================================

def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """
    Verify user credentials.

    Returns the User object on success.
    Returns None on failure.
    """

    email = email.strip().lower()

    user = get_user_by_email(
        db=db,
        email=email,
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user