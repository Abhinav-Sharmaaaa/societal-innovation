from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import (
    SuperAdminSetupRequest,
    UserRegister,
)


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
# Create Public User
# ============================================================

def create_user(
    db: Session,
    user_data: UserRegister,
) -> User:
    """
    Create a new citizen account.

    Public registration always creates a CITIZEN account.
    Privileged accounts are created through protected
    administrative workflows.
    """

    email = user_data.email.strip().lower()

    existing_user = get_user_by_email(
        db=db,
        email=email,
    )

    if existing_user is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    if user_data.phone:
        phone = user_data.phone.strip()

        existing_phone = get_user_by_phone(
            db=db,
            phone=phone,
        )

        if existing_phone is not None:
            raise ValueError(
                "A user with this phone number already exists."
            )
    else:
        phone = None

    password_hash = hash_password(
        user_data.password
    )

    user = User(
        full_name=user_data.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        role=UserRole.CITIZEN,
        organization_id=None,
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
# Create One-Time SUPER_ADMIN
# ============================================================

def create_super_admin(
    db: Session,
    user_data: SuperAdminSetupRequest,
) -> User:
    """
    Create the first and only platform SUPER_ADMIN.

    This function is protected by two mechanisms:

    1. Application-level check:
       No SUPER_ADMIN may already exist.

    2. Database-level unique partial index:
       The database itself prevents a second SUPER_ADMIN.
    """

    # --------------------------------------------------------
    # Check whether a SUPER_ADMIN already exists
    # --------------------------------------------------------

    existing_admin = db.scalar(
        select(User).where(
            User.role == UserRole.SUPER_ADMIN
        )
    )

    if existing_admin is not None:
        raise ValueError(
            "SUPER_ADMIN setup has already been completed."
        )

    # --------------------------------------------------------
    # Normalize email
    # --------------------------------------------------------

    email = user_data.email.strip().lower()

    # --------------------------------------------------------
    # Duplicate email
    # --------------------------------------------------------

    existing_user = get_user_by_email(
        db=db,
        email=email,
    )

    if existing_user is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    # --------------------------------------------------------
    # Normalize/check phone
    # --------------------------------------------------------

    if user_data.phone:
        phone = user_data.phone.strip()

        existing_phone = get_user_by_phone(
            db=db,
            phone=phone,
        )

        if existing_phone is not None:
            raise ValueError(
                "A user with this phone number already exists."
            )
    else:
        phone = None

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    password_hash = hash_password(
        user_data.password
    )

    # --------------------------------------------------------
    # Create SUPER_ADMIN
    # --------------------------------------------------------

    user = User(
        full_name=user_data.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        role=UserRole.SUPER_ADMIN,
        organization_id=None,
        is_active=True,
        is_verified=True,
    )

    db.add(user)

    try:
        db.commit()

    except IntegrityError as error:
        db.rollback()

        # Database-level protection against creating more
        # than one SUPER_ADMIN.
        if "uq_users_single_super_admin" in str(error):
            raise ValueError(
                "SUPER_ADMIN setup has already been completed."
            )

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