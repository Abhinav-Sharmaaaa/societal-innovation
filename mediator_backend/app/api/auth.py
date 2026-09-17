import hmac
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SuperAdminSetupRequest,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_super_admin,
    create_user,
)


class RefreshRequest(BaseModel):
    refresh_token: str


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# Register
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new citizen account.

    Public registration can NEVER create privileged roles.
    """

    try:
        user = create_user(
            db=db,
            user_data=user_data,
        )

        return user

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# ============================================================
# One-Time SUPER_ADMIN Setup
# ============================================================

@router.post(
    "/setup-super-admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def setup_super_admin(
    user_data: SuperAdminSetupRequest,
    db: Session = Depends(get_db),
):
    """
    Create the first and only platform SUPER_ADMIN.

    Requirements:

    1. SUPER_ADMIN_SETUP_KEY must be configured.
    2. The submitted setup key must match.
    3. No SUPER_ADMIN may already exist.

    Once a SUPER_ADMIN exists, this endpoint can no longer
    create another one.
    """

    configured_setup_key = os.getenv(
        "SUPER_ADMIN_SETUP_KEY"
    )

    # --------------------------------------------------------
    # Require server-side setup secret
    # --------------------------------------------------------

    if not configured_setup_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "SUPER_ADMIN setup is not configured on "
                "the server."
            ),
        )

    # --------------------------------------------------------
    # Constant-time secret comparison
    # --------------------------------------------------------

    if not hmac.compare_digest(
        user_data.setup_key,
        configured_setup_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid SUPER_ADMIN setup key.",
        )

    # --------------------------------------------------------
    # Create first SUPER_ADMIN
    # --------------------------------------------------------

    try:
        return create_super_admin(
            db=db,
            user_data=user_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


# ============================================================
# Login
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return access + refresh tokens.
    """

    user = authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
    )

    return LoginResponse(
        user=user,
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        ),
    )


# ============================================================
# Current User
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    return current_user


# ============================================================
# Refresh Token
# ============================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_tokens(
    body: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access + refresh
    token pair (token rotation).

    The client should call this automatically when the access
    token expires (HTTP 401).
    """

    payload = decode_token(body.refresh_token)

    # --------------------------------------------------------
    # Validate refresh token
    # --------------------------------------------------------

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    # --------------------------------------------------------
    # Find and validate user
    # --------------------------------------------------------

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or inactive.",
        )

    # --------------------------------------------------------
    # Issue new token pair (token rotation)
    # --------------------------------------------------------

    new_access_token = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )

    new_refresh_token = create_refresh_token(
        user_id=user.id,
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )