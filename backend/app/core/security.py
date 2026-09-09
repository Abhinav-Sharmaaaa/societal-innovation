import bcrypt


# ============================================================
# Password Hashing Configuration
# ============================================================

BCRYPT_MAX_PASSWORD_BYTES = 72


# ============================================================
# Hash Password
# ============================================================

def hash_password(password: str) -> str:
    """
    Convert a plaintext password into a secure bcrypt hash.

    Bcrypt has a maximum password length of 72 bytes.
    """
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(
            "Password cannot be longer than 72 bytes."
        )

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")


# ============================================================
# Verify Password
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    """

    password_bytes = plain_password.encode("utf-8")

    # Bcrypt only supports passwords up to 72 bytes.
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        return False

    try:
        return bcrypt.checkpw(
            password_bytes,
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False