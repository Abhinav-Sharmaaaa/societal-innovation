from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectMilestoneUpdate(BaseModel):
    progress_percentage: float = Field(
        ge=0,
        le=100,
    )

    status: Literal[
        "NOT_STARTED",
        "IN_PROGRESS",
        "COMPLETED",
        "DELAYED",
        "BLOCKED",
    ]

    completion_remarks: str | None = None


class ProjectMilestoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int

    milestone_type: str
    sequence_number: int

    title: str
    description: str | None
    deliverables: str | None

    start_date: datetime | None
    due_date: datetime | None
    completed_at: datetime | None

    status: str
    progress_percentage: float
    is_mandatory: bool

    completion_remarks: str | None

    created_at: datetime
    updated_at: datetime