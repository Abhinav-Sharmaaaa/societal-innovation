from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


# ============================================================
# Official User Roles
# ============================================================

class OfficialUserRole(str, Enum):
    REVIEW_OFFICER = "REVIEW_OFFICER"

    MUNICIPALITY_OFFICER = "MUNICIPALITY_OFFICER"
    GOVERNMENT_OFFICER = "GOVERNMENT_OFFICER"

    UNIVERSITY_ADMIN = "UNIVERSITY_ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"

    INDUSTRY_ADMIN = "INDUSTRY_ADMIN"
    INDUSTRY_MEMBER = "INDUSTRY_MEMBER"

# ============================================================
# Public User Registration
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
        description="Password for the citizen account",
    )


# ============================================================
# Official User Creation
# ============================================================

class OfficialUserCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the official",
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
        description="Password for the official account",
    )

    role: OfficialUserRole = Field(
        ...,
        description=(
            "Official role assigned by a SUPER_ADMIN."
        ),
    )

    organization_id: int = Field(
        ...,
        gt=0,
        description=(
            "Organization to which the official belongs."
        ),
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

    organization_id: int | None

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
    
# ============================================================
# One-Time SUPER_ADMIN Setup
# ============================================================

class SuperAdminSetupRequest(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the platform SUPER_ADMIN.",
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
        description="Password for the SUPER_ADMIN account.",
    )

    setup_key: str = Field(
        ...,
        min_length=8,
        max_length=256,
        description="Private one-time platform setup key.",
    )