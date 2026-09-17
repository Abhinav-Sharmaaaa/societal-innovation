from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectFundingCreate(BaseModel):
    project_id: int

    transaction_type: Literal[
        "ALLOCATION",
        "DISBURSEMENT",
        "UTILIZATION",
        "REFUND",
    ]

    amount: float = Field(
        gt=0,
    )

    transaction_date: datetime | None = None

    description: str | None = None
    reference_number: str | None = None


class ProjectFundingApproval(BaseModel):
    decision: Literal[
        "APPROVED",
        "REJECTED",
    ]

    remarks: str | None = None


class ProjectFundingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int

    transaction_type: str
    status: str

    amount: float

    transaction_date: datetime | None

    description: str | None
    reference_number: str | None

    created_by: int
    approved_by: int | None
    approved_at: datetime | None

    created_at: datetime
    updated_at: datetime


class ProjectFundingSummary(BaseModel):
    project_id: int

    allocated: float
    disbursed: float
    utilized: float
    refunded: float

    remaining: float