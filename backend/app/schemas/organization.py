from pydantic import BaseModel, ConfigDict, Field

from app.models.challenge import ChallengeCategory
from app.models.organization import OrganizationType


class OrganizationCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    organization_type: OrganizationType

    description: str | None = None

    parent_organization_id: int | None = Field(
        default=None,
        gt=0,
    )

    district: str | None = Field(
        default=None,
        max_length=100,
    )

    locality: str | None = Field(
        default=None,
        max_length=150,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    website: str | None = Field(
        default=None,
        max_length=500,
    )

    competencies: list[ChallengeCategory] = Field(
        default_factory=list,
        description="Challenge categories this organization is capable of handling.",
    )


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    organization_type: OrganizationType
    description: str | None

    parent_organization_id: int | None

    district: str | None
    locality: str | None
    state: str | None

    email: str | None
    phone: str | None
    website: str | None

    is_active: bool