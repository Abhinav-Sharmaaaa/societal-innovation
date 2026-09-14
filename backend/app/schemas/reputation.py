from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReputationScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str

    user_id: int | None
    organization_id: int | None

    total_points: int
    contribution_count: int

    created_at: datetime
    updated_at: datetime


class ReputationEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    entity_type: str

    user_id: int | None
    organization_id: int | None

    event_type: str
    points: int

    description: str | None
    project_id: int | None

    created_at: datetime