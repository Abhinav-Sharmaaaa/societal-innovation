from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.challenge import (
    ChallengeCategory,
    ChallengeLocationSource,
    ChallengeRoutingType,
    ChallengeSeverity,
    ChallengeStatus,
    ChallengeUrgency,
)


# ============================================================
# Evidence Response
# ============================================================

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


# ============================================================
# Challenge Create
# ============================================================

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

    is_anonymous: bool = Field(
        default=False,
        description="If the submitter wants to remain anonymous.",
    )

    category: ChallengeCategory = Field(
        default=ChallengeCategory.OTHER,
        description="Initial category selected by the submitter.",
    )

    urgency: ChallengeUrgency = Field(
        default=ChallengeUrgency.MEDIUM,
        description="Urgency perceived by the submitter.",
    )

    affected_population: int | None = Field(
        default=None,
        ge=0,
    )

    estimated_economic_loss: float | None = Field(
        default=None,
        ge=0,
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    address: str | None = Field(
        default=None,
        max_length=500,
    )

    district: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    locality: str | None = Field(
        default=None,
        max_length=150,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    location_source: ChallengeLocationSource = Field(
        default=ChallengeLocationSource.MANUAL,
        description="How the challenge location was provided.",
    )

    location_verified: bool = Field(
        default=False,
        description="Whether the location was verified through GPS or another trusted resolution process.",
    )

    location_accuracy_meters: float | None = Field(
        default=None,
        ge=0,
        description="Reported GPS accuracy in meters, when available.",
    )

    location_resolution_reason: str | None = Field(
        default=None,
        description="Reason or explanation for the resolved location.",
    )


# ============================================================
# Challenge Update
# ============================================================

class ChallengeUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=20,
    )

    category: ChallengeCategory | None = None

    urgency: ChallengeUrgency | None = None

    affected_population: int | None = Field(
        default=None,
        ge=0,
    )

    estimated_economic_loss: float | None = Field(
        default=None,
        ge=0,
    )

    address: str | None = Field(
        default=None,
        max_length=500,
    )

    district: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


# ============================================================
# Challenge Response
# ============================================================

class ChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # --------------------------------------------------------
    # Basic Information
    # --------------------------------------------------------

    id: int
    title: str
    description: str
    submitted_by: int
    is_anonymous: bool

    # --------------------------------------------------------
    # Location Resolution
    # --------------------------------------------------------

    location_source: ChallengeLocationSource
    location_verified: bool
    location_accuracy_meters: float | None
    locality: str | None
    location_resolution_reason: str | None
    location_resolved_at: datetime | None

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    category: ChallengeCategory
    severity: ChallengeSeverity
    urgency: ChallengeUrgency

    # --------------------------------------------------------
    # Impact / Location
    # --------------------------------------------------------

    affected_population: int | None
    estimated_economic_loss: float | None

    address: str | None
    district: str | None
    state: str | None

    latitude: float | None
    longitude: float | None

    # ========================================================
    # AI / Innovation Analysis
    # ========================================================

    innovation_required: bool

    # --------------------------------------------------------
    # General AI Information
    # --------------------------------------------------------

    ai_confidence_score: float | None
    ai_model_version: str | None

    # --------------------------------------------------------
    # Category Model
    # --------------------------------------------------------

    ai_category_confidence: float | None
    ai_second_category: str | None
    ai_second_category_confidence: float | None
    ai_category_margin: float | None
    ai_category_decision: str | None
    ai_requires_human_review: bool | None
    ai_category_top_3: list[dict] | None

    # --------------------------------------------------------
    # Innovation-required Model
    # --------------------------------------------------------

    ai_innovation_confidence: float | None
    ai_innovation_decision: str | None
    ai_innovation_requires_human_review: bool | None

    # --------------------------------------------------------
    # Innovation-type Model
    # --------------------------------------------------------

    ai_innovation_type: str | None
    ai_innovation_type_confidence: float | None
    ai_innovation_type_second: str | None
    ai_innovation_type_second_confidence: float | None
    ai_innovation_type_margin: float | None
    ai_innovation_type_decision: str | None
    ai_innovation_type_requires_human_review: bool | None
    ai_innovation_type_top_3: list[dict] | None

    # --------------------------------------------------------
    # AI Analysis Timestamp
    # --------------------------------------------------------

    ai_analysis_at: datetime | None

    # ========================================================
    # Routing
    # ========================================================

    routing_type: ChallengeRoutingType
    routing_reason: str | None

    # --------------------------------------------------------
    # Current Authority Assignment
    # --------------------------------------------------------

    current_authority_id: int | None
    assigned_at: datetime | None
    assigned_by: int | None

    # --------------------------------------------------------
    # Challenge Lifecycle
    # --------------------------------------------------------

    status: ChallengeStatus

    # --------------------------------------------------------
    # Duplicate / Master Challenge
    # --------------------------------------------------------

    is_master_challenge: bool
    master_challenge_id: int | None
    duplicate_similarity_score: float | None

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence: list[ChallengeEvidenceResponse] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at: datetime
    updated_at: datetime