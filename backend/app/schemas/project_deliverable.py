from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectDeliverableCreate(BaseModel):
    milestone_id: int

    title: str = Field(
        min_length=5,
        max_length=255,
    )

    description: str | None = None

    due_date: datetime | None = None

    is_mandatory: bool = True


class ProjectDeliverableSubmit(BaseModel):
    submission_reference: str = Field(
        min_length=3,
    )


class ProjectDeliverableReview(BaseModel):
    decision: Literal[
        "APPROVED",
        "REJECTED",
    ]

    review_remarks: str | None = None


class ProjectDeliverableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    milestone_id: int

    title: str
    description: str | None

    due_date: datetime | None
    submitted_at: datetime | None
    approved_at: datetime | None

    status: str

    submission_reference: str | None
    review_remarks: str | None

    is_mandatory: bool

    created_at: datetime
    updated_at: datetime