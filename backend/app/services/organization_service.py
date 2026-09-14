from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import ChallengeCategory
from app.models.organization import Organization
from app.models.organization_competency import OrganizationCompetency
from app.schemas.organization import OrganizationCreate
from app.schemas.organization_competency import (
    OrganizationCompetencyCreate,
)


# ============================================================
# Create Organization
# ============================================================

def create_organization(
    db: Session,
    organization_data: OrganizationCreate,
) -> Organization:

    # --------------------------------------------------------
    # Validate parent organization
    # --------------------------------------------------------

    if organization_data.parent_organization_id is not None:
        parent = db.get(
            Organization,
            organization_data.parent_organization_id,
        )

        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent organization not found.",
            )

        if not parent.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent organization is inactive.",
            )

    # --------------------------------------------------------
    # Prevent obvious duplicates
    # --------------------------------------------------------

    existing = db.scalars(
        select(Organization).where(
            Organization.name == organization_data.name,
            Organization.organization_type
            == organization_data.organization_type,
            Organization.district == organization_data.district,
            Organization.state == organization_data.state,
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An organization with the same name "
                "and location already exists."
            ),
        )

    # --------------------------------------------------------
    # Create organization
    # --------------------------------------------------------

    organization = Organization(
        name=organization_data.name,
        organization_type=organization_data.organization_type,
        description=organization_data.description,
        parent_organization_id=(
            organization_data.parent_organization_id
        ),
        district=organization_data.district,
        locality=organization_data.locality,
        state=organization_data.state,
        email=organization_data.email,
        phone=organization_data.phone,
        website=organization_data.website,
    )

    db.add(organization)
    db.flush()

    # --------------------------------------------------------
    # Add competencies
    # --------------------------------------------------------

    unique_categories = set(
        organization_data.competencies
    )

    for category in unique_categories:
        organization.competencies.append(
            OrganizationCompetency(
                category=category,
            )
        )

    db.commit()
    db.refresh(organization)

    return organization


# ============================================================
# Get Organizations
# ============================================================

def get_organizations(
    db: Session,
    organization_type=None,
    district: str | None = None,
    state: str | None = None,
) -> list[Organization]:

    statement = select(Organization).where(
        Organization.is_active.is_(True)
    )

    if organization_type is not None:
        statement = statement.where(
            Organization.organization_type
            == organization_type
        )

    if district is not None:
        statement = statement.where(
            Organization.district == district
        )

    if state is not None:
        statement = statement.where(
            Organization.state == state
        )

    statement = statement.order_by(
        Organization.name
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# Get Organization
# ============================================================

def get_organization_by_id(
    db: Session,
    organization_id: int,
) -> Organization | None:

    return db.get(
        Organization,
        organization_id,
    )


# ============================================================
# Add Competency
# ============================================================

def add_organization_competency(
    db: Session,
    organization_id: int,
    competency_data: OrganizationCompetencyCreate,
) -> OrganizationCompetency:

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

    existing = db.scalars(
        select(OrganizationCompetency).where(
            OrganizationCompetency.organization_id
            == organization_id,
            OrganizationCompetency.category
            == competency_data.category,
        )
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This organization already has "
                "this competency."
            ),
        )

    competency = OrganizationCompetency(
        organization_id=organization_id,
        category=competency_data.category,
    )

    db.add(competency)
    db.commit()
    db.refresh(competency)

    return competency


# ============================================================
# Get Organization Competencies
# ============================================================

def get_organization_competencies(
    db: Session,
    organization_id: int,
) -> list[OrganizationCompetency]:

    organization = db.get(
        Organization,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    statement = (
        select(OrganizationCompetency)
        .where(
            OrganizationCompetency.organization_id
            == organization_id
        )
        .order_by(
            OrganizationCompetency.category
        )
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# Remove Organization Competency
# ============================================================

def remove_organization_competency(
    db: Session,
    organization_id: int,
    category: ChallengeCategory,
) -> None:

    competency = db.scalars(
        select(OrganizationCompetency).where(
            OrganizationCompetency.organization_id
            == organization_id,
            OrganizationCompetency.category
            == category,
        )
    ).first()

    if competency is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "This organization does not have "
                "the requested competency."
            ),
        )

    db.delete(competency)
    db.commit()