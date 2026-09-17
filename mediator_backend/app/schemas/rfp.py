from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.rfp import RFPStatus


class RFPCreate(BaseModel):
    innovation_opportunity_id: int = Field(
        ...,
        gt=0,
    )

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )

    description: str = Field(
        ...,
        min_length=10,
    )

    objectives: str | None = None
    technical_requirements: str | None = None
    expected_outcomes: str | None = None

    estimated_budget: float | None = Field(
        default=None,
        ge=0,
    )

    expected_duration_days: int | None = Field(
        default=None,
        gt=0,
    )

    proposal_deadline: datetime | None = None


class RFPResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    innovation_opportunity_id: int
    created_by: int

    title: str
    description: str
    objectives: str | None
    technical_requirements: str | None
    expected_outcomes: str | None

    estimated_budget: float | None
    expected_duration_days: int | None
    proposal_deadline: datetime | None

    status: RFPStatus
    is_active: bool

    published_at: datetime | None
    closed_at: datetime | None

    created_at: datetime
    updated_at: datetime