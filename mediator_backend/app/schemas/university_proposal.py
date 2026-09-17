from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.university_proposal import (
    UniversityProposalStatus,
)


class UniversityProposalCreate(BaseModel):
    invitation_id: int = Field(
        ...,
        gt=0,
    )

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
    )

    solution: str = Field(
        ...,
        min_length=20,
    )

    technical_approach: str = Field(
        ...,
        min_length=20,
    )

    research_methodology: str | None = None

    required_resources: str | None = None

    estimated_cost: float | None = Field(
        default=None,
        ge=0,
    )

    expected_timeline_days: int | None = Field(
        default=None,
        gt=0,
    )

    faculty_team: str | None = None

    expected_outcomes: str | None = None

    technology_requirements: str | None = None


class UniversityProposalResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    rfp_id: int
    invitation_id: int
    university_id: int
    submitted_by: int

    title: str
    solution: str
    technical_approach: str
    research_methodology: str | None

    required_resources: str | None
    estimated_cost: float | None
    expected_timeline_days: int | None

    faculty_team: str | None
    expected_outcomes: str | None
    technology_requirements: str | None

    status: UniversityProposalStatus

    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime