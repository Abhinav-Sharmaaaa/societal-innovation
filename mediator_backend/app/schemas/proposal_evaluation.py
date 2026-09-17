from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProposalEvaluationCreate(BaseModel):
    proposal_id: int

    technical_feasibility_score: float = Field(
        ge=0,
        le=100,
    )

    innovation_score: float = Field(
        ge=0,
        le=100,
    )

    cost_effectiveness_score: float = Field(
        ge=0,
        le=100,
    )

    impact_score: float = Field(
        ge=0,
        le=100,
    )

    timeline_score: float = Field(
        ge=0,
        le=100,
    )

    scalability_score: float = Field(
        ge=0,
        le=100,
    )

    research_capability_score: float = Field(
        ge=0,
        le=100,
    )

    remarks: str | None = None


class ProposalEvaluationDecisionRequest(BaseModel):
    decision: Literal[
        "SHORTLISTED",
        "REJECTED",
    ]

    remarks: str | None = None


class ProposalEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    evaluated_by: int

    technical_feasibility_score: float
    innovation_score: float
    cost_effectiveness_score: float
    impact_score: float
    timeline_score: float
    scalability_score: float
    research_capability_score: float

    overall_score: float

    remarks: str | None
    decision: str

    evaluated_at: datetime
    created_at: datetime
    updated_at: datetime