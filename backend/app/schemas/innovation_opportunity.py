from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.innovation_opportunity import (
    InnovationOpportunityStatus,
)


# ============================================================
# Create
# ============================================================

class InnovationOpportunityCreate(BaseModel):
    challenge_id: int = Field(
        ...,
        gt=0,
    )

    sponsoring_organization_id: int = Field(
        ...,
        gt=0,
    )

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )

    problem_statement: str = Field(
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


# ============================================================
# Response
# ============================================================

class InnovationOpportunityResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    challenge_id: int
    sponsoring_organization_id: int

    created_by: int
    approved_by: int | None

    title: str
    problem_statement: str
    objectives: str | None
    technical_requirements: str | None
    expected_outcomes: str | None

    estimated_budget: float | None
    expected_duration_days: int | None
    proposal_deadline: datetime | None

    status: InnovationOpportunityStatus
    is_active: bool

    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime