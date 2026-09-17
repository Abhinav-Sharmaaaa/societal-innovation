from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings


# ============================================================
# Create Access Token
# ============================================================

def create_access_token(
    user_id: int,
    role: str,
) -> str:
    """
    Create a short-lived JWT access token.
    """

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ============================================================
# Create Refresh Token
# ============================================================

def create_refresh_token(
    user_id: int,
) -> str:
    """
    Create a longer-lived JWT refresh token.
    """

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ============================================================
# Decode Token
# ============================================================

def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT.

    Returns the payload when valid.
    Returns None when invalid or expired.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload

    except JWTError:
        return None