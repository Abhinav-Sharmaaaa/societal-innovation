from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.challenge_assignment import (
    AssignmentAction,
    AssignmentStatus,
)


class ChallengeAssignmentCreate(BaseModel):
    authority_id: int = Field(
        ...,
        gt=0,
        description="Organization ID that should receive the challenge.",
    )

    remarks: str | None = Field(
        default=None,
        max_length=2000,
    )


class ChallengeReassignRequest(BaseModel):
    authority_id: int = Field(
        ...,
        gt=0,
        description="Organization ID that should receive the reassigned challenge.",
    )

    reason: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Reason for changing the current authority.",
    )

    remarks: str | None = Field(
        default=None,
        max_length=2000,
    )


class ChallengeEscalateRequest(BaseModel):
    authority_id: int = Field(
        ...,
        gt=0,
        description="Higher-level organization that should receive the challenge.",
    )

    reason: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Reason the current authority cannot resolve the challenge.",
    )

    remarks: str | None = Field(
        default=None,
        max_length=2000,
    )


class ChallengeAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: int

    from_authority_id: int | None
    to_authority_id: int

    performed_by: int | None

    action: AssignmentAction
    status: AssignmentStatus

    reason: str | None
    remarks: str | None

    created_at: datetime
    completed_at: datetime | None