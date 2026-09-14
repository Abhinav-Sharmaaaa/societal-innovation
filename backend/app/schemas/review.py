from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.challenge_review import ReviewDecision


class ReviewOverrideRequest(BaseModel):
    authority_id: int = Field(
        ...,
        gt=0,
        description="Authority selected by the reviewer.",
    )

    reason: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Reason for overriding the AI recommendation.",
    )


class ReviewDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    challenge_id: int
    reviewer_id: int

    decision: ReviewDecision

    recommended_authority_id: int | None
    selected_authority_id: int

    reason: str | None
    created_at: datetime