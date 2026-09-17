from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization, OrganizationType
from app.models.organization_capability import (
    CapabilityType,
    OrganizationCapability,
)
from app.schemas.organization_capability import (
    OrganizationCapabilityCreate,
)


# ============================================================
# Validate Organization
# ============================================================

def _get_active_organization(
    db: Session,
    organization_id: int,
) -> Organization:

    organization = db.get(
        Organization,
        organization_id,
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

    return organization


# ============================================================
# Validate Capability Type Against Organization Type
# ============================================================

def _validate_capability_type(
    organization: Organization,
    capability_type: CapabilityType,
) -> None:

    is_university_capability = (
        capability_type.value.startswith("UNIVERSITY_")
    )

    is_industry_capability = (
        capability_type.value.startswith("INDUSTRY_")
    )

    if (
        is_university_capability
        and organization.organization_type
        != OrganizationType.UNIVERSITY
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "University capability types can only be "
                "assigned to UNIVERSITY organizations."
            ),
        )

    if (
        is_industry_capability
        and organization.organization_type
        != OrganizationType.INDUSTRY
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Industry capability types can only be "
                "assigned to INDUSTRY organizations."
            ),
        )


# ============================================================
# Add Capability
# ============================================================

def add_organization_capability(
    db: Session,
    organization_id: int,
    capability_data: OrganizationCapabilityCreate,
) -> OrganizationCapability:

    organization = _get_active_organization(
        db=db,
        organization_id=organization_id,
    )

    _validate_capability_type(
        organization=organization,
        capability_type=capability_data.capability_type,
    )

    existing = db.scalars(
        select(OrganizationCapability).where(
            OrganizationCapability.organization_id
            == organization_id,
            OrganizationCapability.capability_type
            == capability_data.capability_type,
            OrganizationCapability.name
            == capability_data.name,
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This organization already has "
                "this capability."
            ),
        )

    capability = OrganizationCapability(
        organization_id=organization_id,
        capability_type=capability_data.capability_type,
        name=capability_data.name,
        description=capability_data.description,
    )

    db.add(capability)
    db.commit()
    db.refresh(capability)

    return capability


# ============================================================
# List Capabilities
# ============================================================

def get_organization_capabilities(
    db: Session,
    organization_id: int,
) -> list[OrganizationCapability]:

    _get_active_organization(
        db=db,
        organization_id=organization_id,
    )

    statement = (
        select(OrganizationCapability)
        .where(
            OrganizationCapability.organization_id
            == organization_id
        )
        .order_by(
            OrganizationCapability.capability_type,
            OrganizationCapability.name,
        )
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# Delete Capability
# ============================================================

def remove_organization_capability(
    db: Session,
    organization_id: int,
    capability_id: int,
) -> None:

    capability = db.get(
        OrganizationCapability,
        capability_id,
    )

    if capability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization capability not found.",
        )

    if capability.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization capability not found.",
        )

    db.delete(capability)
    db.commit()