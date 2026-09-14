from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.rfp_invitation import RFPInvitationStatus


class RFPInvitationCreate(BaseModel):
    rfp_id: int = Field(
        ...,
        gt=0,
    )

    university_id: int = Field(
        ...,
        gt=0,
    )


class RFPInvitationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    rfp_id: int
    university_id: int
    invited_by: int

    recommendation_rank: int | None
    match_score: float | None

    status: RFPInvitationStatus

    response_reason: str | None

    invited_at: datetime
    viewed_at: datetime | None
    responded_at: datetime | None

    created_at: datetime
    updated_at: datetime


class RFPInvitationDecision(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=2000,
    )