from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


# ============================================================
# User Registration
# ============================================================

class UserRegister(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the user",
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password",
    )

    role: UserRole = Field(
        default=UserRole.CITIZEN,
        description="Role assigned to the user",
    )


# ============================================================
# Login Request
# ============================================================

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


# ============================================================
# User Response
# ============================================================

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool
    is_verified: bool


# ============================================================
# Token Response
# ============================================================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ============================================================
# Login Response
# ============================================================

class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse