from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.challenge import (
    ChallengeCategory,
    ChallengeSeverity,
    ChallengeStatus,
    ChallengeUrgency,
    ChallengeRoutingType,
)


class ChallengeEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evidence_type: str
    original_filename: str
    content_type: str | None
    file_size: int | None
    file_url: str | None
    uploaded_by: int
    created_at: datetime


class ChallengeCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Short title describing the challenge.",
    )

    description: str = Field(
        ...,
        min_length=20,
        description="Detailed description of the societal challenge.",
    )

    category: ChallengeCategory = Field(
        default=ChallengeCategory.OTHER,
        description="Initial category selected by the submitter.",
    )

    urgency: ChallengeUrgency = Field(
        default=ChallengeUrgency.MEDIUM,
        description="Urgency perceived by the submitter.",
    )

    affected_population: int | None = Field(default=None, ge=0)
    estimated_economic_loss: float | None = Field(default=None, ge=0)

    address: str | None = Field(default=None, max_length=500)
    district: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)

    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ChallengeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    description: str | None = Field(default=None, min_length=20)
    category: ChallengeCategory | None = None
    urgency: ChallengeUrgency | None = None
    affected_population: int | None = Field(default=None, ge=0)
    estimated_economic_loss: float | None = Field(default=None, ge=0)
    address: str | None = Field(default=None, max_length=500)
    district: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    submitted_by: int

    category: ChallengeCategory
    severity: ChallengeSeverity
    urgency: ChallengeUrgency

    affected_population: int | None
    estimated_economic_loss: float | None

    address: str | None
    district: str | None
    state: str | None

    latitude: float | None
    longitude: float | None

    # --------------------------------------------------------
    # AI Analysis
    # --------------------------------------------------------

    innovation_required: bool

    ai_confidence_score: float | None
    ai_model_version: str | None

    ai_category_confidence: float | None
    ai_second_category: str | None
    ai_second_category_confidence: float | None
    ai_category_margin: float | None
    ai_category_decision: str | None
    ai_requires_human_review: bool | None
    ai_category_top_3: list[dict] | None
    ai_analysis_at: datetime | None

    # --------------------------------------------------------
    # Routing
    # --------------------------------------------------------

    routing_type: ChallengeRoutingType
    routing_reason: str | None

    status: ChallengeStatus

    is_master_challenge: bool
    master_challenge_id: int | None
    duplicate_similarity_score: float | None

    evidence: list[ChallengeEvidenceResponse] = Field(
        default_factory=list
    )

    created_at: datetime
    updated_at: datetime
