from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectOutcomeCreate(BaseModel):
    project_id: int

    title: str = Field(
        min_length=5,
        max_length=255,
    )

    description: str = Field(
        min_length=20,
    )

    beneficiary_count: int | None = Field(
        default=None,
        ge=0,
    )

    metric_name: str | None = Field(
        default=None,
        max_length=255,
    )

    metric_type: Literal[
        "COUNT",
        "PERCENTAGE",
        "CURRENCY",
        "SCORE",
        "TEXT",
    ] | None = None

    baseline_value: float | None = None
    target_value: float | None = None
    achieved_value: float | None = None

    impact_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class ProjectOutcomeVerification(BaseModel):
    decision: Literal[
        "VERIFIED",
        "REJECTED",
    ]

    verification_remarks: str | None = None


class ProjectOutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    submitted_by: int

    title: str
    description: str

    beneficiary_count: int | None

    metric_name: str | None
    metric_type: str | None

    baseline_value: float | None
    target_value: float | None
    achieved_value: float | None

    impact_score: float | None

    status: str

    submitted_at: datetime | None
    verified_at: datetime | None
    verification_remarks: str | None

    created_at: datetime
    updated_at: datetime