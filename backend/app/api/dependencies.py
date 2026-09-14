from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.jwt import decode_token
from app.db.database import get_db
from app.models.user import User, UserRole


# ============================================================
# HTTP Bearer Authentication
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=False,
)


# ============================================================
# Database Dependency
# ============================================================

def get_database(
    db: Session = Depends(get_db),
) -> Generator[Session, None, None]:
    """
    Provide a database session to an API endpoint.

    This wrapper gives us a consistent dependency name that
    can be used throughout the API layer.
    """

    yield db


# ============================================================
# Current User
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_database),
) -> User:
    """
    Authenticate the current request using a JWT access token.

    Steps:
        1. Read Authorization: Bearer <token>
        2. Decode and validate JWT
        3. Ensure token is an access token
        4. Find the user
        5. Ensure the account is active
    """

    # --------------------------------------------------------
    # No Authorization header
    # --------------------------------------------------------

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # --------------------------------------------------------
    # Decode JWT
    # --------------------------------------------------------

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # Ensure this is an access token
    # --------------------------------------------------------

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # Extract user ID
    # --------------------------------------------------------

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # Ensure account is active
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return user


# ============================================================
# SUPER_ADMIN Access
# ============================================================

def require_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Restrict an endpoint to the platform-level SUPER_ADMIN.
    """

    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SUPER_ADMIN access required.",
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return current_user


# ============================================================
# Role-Based Access Control
# ============================================================

def require_roles(
    *allowed_roles: UserRole,
):
    """
    Create a dependency that restricts an endpoint to
    specific user roles.

    Example:

        @router.get(
            "/admin",
            dependencies=[
                Depends(
                    require_roles(UserRole.SUPER_ADMIN)
                )
            ]
        )
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker