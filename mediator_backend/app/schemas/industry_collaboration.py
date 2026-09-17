from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class IndustryCollaborationCreate(BaseModel):
    university_proposal_id: int

    title: str = Field(
        min_length=5,
        max_length=255,
    )

    collaboration_description: str = Field(
        min_length=20,
    )

    funding_amount: float | None = Field(
        default=None,
        ge=0,
    )

    technical_mentorship: str | None = None
    industry_experts: str | None = None
    infrastructure_resources: str | None = None
    technology_support: str | None = None
    internship_support: str | None = None
    pilot_deployment_support: str | None = None
    commercialization_support: str | None = None

    proposed_duration_days: int | None = Field(
        default=None,
        gt=0,
    )
    
    response_deadline: datetime | None = None

    additional_terms: str | None = None


class IndustryCollaborationDecisionRequest(BaseModel):
    decision: Literal[
        "ACCEPTED",
        "REJECTED",
        "MODIFICATION_REQUESTED",
    ]

    remarks: str | None = None


class IndustryCollaborationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    university_proposal_id: int
    industry_id: int
    submitted_by: int

    title: str
    collaboration_description: str

    funding_amount: float | None

    technical_mentorship: str | None
    industry_experts: str | None
    infrastructure_resources: str | None
    technology_support: str | None
    internship_support: str | None
    pilot_deployment_support: str | None
    commercialization_support: str | None

    proposed_duration_days: int | None
    response_deadline: datetime | None
    additional_terms: str | None

    status: str

    submitted_at: datetime | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime