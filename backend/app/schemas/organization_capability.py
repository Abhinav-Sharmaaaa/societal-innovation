from pydantic import BaseModel, ConfigDict, Field

from app.models.organization_capability import CapabilityType


class OrganizationCapabilityCreate(BaseModel):
    capability_type: CapabilityType

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    description: str | None = None


class OrganizationCapabilityResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    organization_id: int
    capability_type: CapabilityType
    name: str
    description: str | None