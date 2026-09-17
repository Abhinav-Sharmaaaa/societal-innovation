from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TriageRoutingType(str, Enum):
    MUNICIPALITY = "MUNICIPALITY"
    GOVERNMENT = "GOVERNMENT"
    INNOVATION = "INNOVATION"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    challenge_id: int | None = Field(
        default=None,
        ge=1,
        description="Existing challenge ID to persist AI analysis for.",
    )

    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1)
    category: str | None = None
    affected_population: int | None = Field(default=None, ge=0)
    estimated_economic_loss: float | None = Field(default=None, ge=0)
    address: str | None = None
    district: str | None = None
    state: str | None = None


class CategoryPrediction(BaseModel):
    rank: int = Field(ge=1)
    category: str
    confidence: float = Field(ge=0.0, le=1.0)


class InnovationTypePrediction(BaseModel):
    rank: int = Field(ge=1)
    innovation_type: str
    confidence: float = Field(ge=0.0, le=1.0)


class TriageResponse(BaseModel):
    # ============================================================
    # CATEGORY
    # ============================================================

    category: str

    category_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    second_category: str

    second_category_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    category_margin: float = Field(
        ge=-1.0,
        le=1.0,
    )

    category_top_3: list[CategoryPrediction]

    category_decision: str

    requires_human_review: bool

    # ============================================================
    # SEVERITY / URGENCY
    # ============================================================

    severity: str
    urgency: str

    # ============================================================
    # INNOVATION REQUIRED
    # ============================================================

    innovation_required: bool

    innovation_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    innovation_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    innovation_decision: str

    innovation_requires_human_review: bool

    # ============================================================
    # INNOVATION TYPE
    # ============================================================

    innovation_type: str

    innovation_type_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    innovation_type_second: str | None = None

    innovation_type_second_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    innovation_type_margin: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
    )

    innovation_type_decision: str

    innovation_type_requires_human_review: bool

    innovation_type_top_3: list[
        InnovationTypePrediction
    ]

    # ============================================================
    # ROUTING
    # ============================================================

    routing_type: TriageRoutingType

    routing_confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    # ============================================================
    # SCORES
    # ============================================================

    severity_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    urgency_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    # ============================================================
    # EXPLANATIONS
    # ============================================================

    routing_reason: str
    severity_reason: str
    urgency_reason: str
    innovation_reason: str

    # ============================================================
    # MODEL VERSION
    # ============================================================

    model_version: str