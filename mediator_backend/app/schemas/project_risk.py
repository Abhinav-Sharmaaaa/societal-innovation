from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

class ProjectRiskActionRequest(BaseModel):
    action: Literal[
        "ACKNOWLEDGED",
        "MITIGATED",
        "CLOSED",
    ]

    remarks: str | None = None

class ProjectRiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int

    risk_level: str
    risk_score: float

    title: str
    description: str

    detected_factors: str | None
    recommended_action: str | None

    status: str

    detected_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    resolution_remarks: str | None

    created_at: datetime
    updated_at: datetime
    
