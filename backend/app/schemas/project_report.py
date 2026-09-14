from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectReportCreate(BaseModel):
    project_id: int
    milestone_id: int | None = None

    report_type: Literal[
        "PROGRESS",
        "MILESTONE",
        "FINANCIAL",
        "PILOT",
        "FINAL",
    ]

    title: str = Field(
        min_length=5,
        max_length=255,
    )

    summary: str = Field(
        min_length=20,
    )

    findings: str | None = None
    challenges: str | None = None
    next_steps: str | None = None


class ProjectReportReview(BaseModel):
    decision: Literal[
        "APPROVED",
        "REJECTED",
    ]

    review_remarks: str | None = None


class ProjectReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    milestone_id: int | None
    submitted_by: int

    report_type: str
    title: str
    summary: str

    findings: str | None
    challenges: str | None
    next_steps: str | None

    status: str

    submitted_at: datetime | None
    reviewed_at: datetime | None
    review_remarks: str | None

    created_at: datetime
    updated_at: datetime