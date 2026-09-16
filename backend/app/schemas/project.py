from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    collaboration_id: int

    title: str = Field(
        min_length=5,
        max_length=255,
    )

    description: str | None = None
    objectives: str | None = None
    expected_outcomes: str | None = None

    total_budget: float | None = Field(
        default=None,
        ge=0,
    )

    start_date: datetime | None = None
    target_completion_date: datetime | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    collaboration_id: int
    challenge_id: int

    university_id: int
    industry_id: int

    created_by: int

    title: str
    description: str | None
    objectives: str | None
    expected_outcomes: str | None

    total_budget: float | None

    start_date: datetime | None
    target_completion_date: datetime | None
    actual_completion_date: datetime | None

    status: str
    health: str
    progress_percentage: float

    created_at: datetime
    updated_at: datetime
    
class ProjectListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: str
    health: str
    progress_percentage: float
    start_date: datetime | None
    target_completion_date: datetime | None