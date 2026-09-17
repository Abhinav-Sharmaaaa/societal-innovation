from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectEvidenceCreate(BaseModel):
    project_id: int
    report_id: int | None = None

    evidence_type: Literal[
        "DOCUMENT",
        "IMAGE",
        "VIDEO",
        "DATASET",
        "LINK",
    ]

    title: str = Field(
        min_length=3,
        max_length=255,
    )

    file_url: str | None = None
    external_url: str | None = None
    description: str | None = None


class ProjectEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    report_id: int | None
    uploaded_by: int

    evidence_type: str
    title: str

    file_url: str | None
    external_url: str | None
    description: str | None

    created_at: datetime
    updated_at: datetime