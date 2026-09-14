from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.organization import Organization, OrganizationType
from app.models.user import User
from app.schemas.auth import OfficialUserCreate, OfficialUserRole
from app.services.auth_service import (
    get_user_by_email,
    get_user_by_phone,
)


# ============================================================
# Role → Organization Compatibility
# ============================================================

ROLE_ORGANIZATION_MAP = {
    OfficialUserRole.REVIEW_OFFICER: {
        OrganizationType.MUNICIPALITY,
        OrganizationType.GOVERNMENT_DEPARTMENT,
    },

    OfficialUserRole.MUNICIPALITY_OFFICER: {
        OrganizationType.MUNICIPALITY,
    },

    OfficialUserRole.GOVERNMENT_OFFICER: {
        OrganizationType.GOVERNMENT_DEPARTMENT,
    },

    OfficialUserRole.UNIVERSITY_ADMIN: {
        OrganizationType.UNIVERSITY,
    },

    OfficialUserRole.FACULTY: {
        OrganizationType.UNIVERSITY,
    },

    OfficialUserRole.STUDENT: {
        OrganizationType.UNIVERSITY,
    },

    OfficialUserRole.INDUSTRY_ADMIN: {
        OrganizationType.INDUSTRY,
    },

    OfficialUserRole.INDUSTRY_MEMBER: {
        OrganizationType.INDUSTRY,
    },
}


def create_official_user(
    db: Session,
    user_data: OfficialUserCreate,
) -> User:
    """
    Create an official account under an existing organization.

    This function is intended to be called only by a
    SUPER_ADMIN-protected API endpoint.
    """

    # --------------------------------------------------------
    # Normalize email
    # --------------------------------------------------------

    email = user_data.email.strip().lower()

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

    if get_user_by_email(
        db=db,
        email=email,
    ) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # --------------------------------------------------------
    # Normalize and check phone
    # --------------------------------------------------------

    phone = (
        user_data.phone.strip()
        if user_data.phone
        else None
    )

    if phone is not None:
        if get_user_by_phone(
            db=db,
            phone=phone,
        ) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this phone number already exists.",
            )

    # --------------------------------------------------------
    # Get organization
    # --------------------------------------------------------

    organization = db.get(
        Organization,
        user_data.organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is inactive.",
        )

    # --------------------------------------------------------
    # Validate role ↔ organization type
    # --------------------------------------------------------

    allowed_types = ROLE_ORGANIZATION_MAP.get(
        user_data.role
    )

    if allowed_types is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid official role.",
        )

    if organization.organization_type not in allowed_types:
        allowed_names = ", ".join(
            sorted(
                organization_type.value
                for organization_type in allowed_types
            )
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Role {user_data.role.value} is not compatible "
                f"with organization type "
                f"{organization.organization_type.value}. "
                f"Expected: {allowed_names}."
            ),
        )

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    password_hash = hash_password(
        user_data.password
    )

    # --------------------------------------------------------
    # Create official user
    # --------------------------------------------------------

    user = User(
        full_name=user_data.full_name.strip(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        role=user_data.role.value,
        organization_id=organization.id,
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user