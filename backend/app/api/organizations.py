from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import require_super_admin
from app.db.database import get_db
from app.models.challenge import ChallengeCategory
from app.models.organization import OrganizationType
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
)
from app.schemas.organization_competency import (
    OrganizationCompetencyCreate,
    OrganizationCompetencyResponse,
)
from app.services.organization_service import (
    add_organization_competency,
    create_organization,
    get_organization_by_id,
    get_organization_competencies,
    get_organizations,
    remove_organization_competency,
)

from app.schemas.organization_capability import (
    OrganizationCapabilityCreate,
    OrganizationCapabilityResponse,
)

from app.services.organization_capability_service import (
    add_organization_capability,
    get_organization_capabilities,
    remove_organization_capability,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


# ============================================================
# Create Organization
# ============================================================

@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_organization(
    organization_data: OrganizationCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Create an organization/authority.

    Only the platform SUPER_ADMIN can create organizations.
    """

    return create_organization(
        db=db,
        organization_data=organization_data,
    )


# ============================================================
# List Organizations
# ============================================================

@router.get(
    "",
    response_model=list[OrganizationResponse],
)
async def list_organization_records(
    organization_type: OrganizationType | None = Query(
        default=None,
    ),
    district: str | None = Query(
        default=None,
    ),
    state: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    """
    List active organizations with optional filters.
    """

    return get_organizations(
        db=db,
        organization_type=organization_type,
        district=district,
        state=state,
    )


# ============================================================
# Get Organization
# ============================================================

@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single organization.
    """

    organization = get_organization_by_id(
        db=db,
        organization_id=organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization


# ============================================================
# Add Organization Competency
# ============================================================

@router.post(
    "/{organization_id}/competencies",
    response_model=OrganizationCompetencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_competency(
    organization_id: int,
    competency_data: OrganizationCompetencyCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Add a challenge category competency to an organization.

    Only the platform SUPER_ADMIN can modify organization
    competencies.
    """

    return add_organization_competency(
        db=db,
        organization_id=organization_id,
        competency_data=competency_data,
    )


# ============================================================
# Get Organization Competencies
# ============================================================

@router.get(
    "/{organization_id}/competencies",
    response_model=list[OrganizationCompetencyResponse],
)
async def list_competencies(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Return all challenge categories handled by an organization.
    """

    return get_organization_competencies(
        db=db,
        organization_id=organization_id,
    )


# ============================================================
# Remove Organization Competency
# ============================================================

@router.delete(
    "/{organization_id}/competencies/{category}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_competency(
    organization_id: int,
    category: ChallengeCategory,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Remove a challenge category competency from an organization.

    Only the platform SUPER_ADMIN can modify organization
    competencies.
    """

    remove_organization_competency(
        db=db,
        organization_id=organization_id,
        category=category,
    )

    return None

# ============================================================
# Add Organization Capability
# ============================================================

@router.post(
    "/{organization_id}/capabilities",
    response_model=OrganizationCapabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_capability(
    organization_id: int,
    capability_data: OrganizationCapabilityCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Add a university or industry capability.

    Only SUPER_ADMIN can modify organization capabilities.
    """

    return add_organization_capability(
        db=db,
        organization_id=organization_id,
        capability_data=capability_data,
    )
    
# ============================================================
# List Organization Capabilities
# ============================================================

@router.get(
    "/{organization_id}/capabilities",
    response_model=list[OrganizationCapabilityResponse],
)
async def list_capabilities(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Return all collaboration capabilities
    registered for an organization.
    """

    return get_organization_capabilities(
        db=db,
        organization_id=organization_id,
    )
    
# ============================================================
# Remove Organization Capability
# ============================================================

@router.delete(
    "/{organization_id}/capabilities/{capability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_capability(
    organization_id: int,
    capability_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """
    Remove an organization capability.

    Only SUPER_ADMIN can modify organization capabilities.
    """

    remove_organization_capability(
        db=db,
        organization_id=organization_id,
        capability_id=capability_id,
    )

    return None