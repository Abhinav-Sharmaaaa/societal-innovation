from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.challenge_evidence import ChallengeEvidence
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.innovation_opportunity import InnovationOpportunity


# ============================================================
# Challenge Enums
# ============================================================


class ChallengeCategory(str, Enum):
    WATER = "WATER"
    SANITATION = "SANITATION"
    WASTE_MANAGEMENT = "WASTE_MANAGEMENT"
    HEALTHCARE = "HEALTHCARE"
    EDUCATION = "EDUCATION"
    AGRICULTURE = "AGRICULTURE"
    TRANSPORTATION = "TRANSPORTATION"
    ENERGY = "ENERGY"
    ENVIRONMENT = "ENVIRONMENT"
    PUBLIC_SAFETY = "PUBLIC_SAFETY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    DIGITAL_SERVICES = "DIGITAL_SERVICES"
    EMPLOYMENT = "EMPLOYMENT"
    SOCIAL_WELFARE = "SOCIAL_WELFARE"
    DISASTER_MANAGEMENT = "DISASTER_MANAGEMENT"
    OTHER = "OTHER"


class ChallengeStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_AI_ANALYSIS = "UNDER_AI_ANALYSIS"
    UNDER_REVIEW = "UNDER_REVIEW"
    ROUTED = "ROUTED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class ChallengeUrgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChallengeSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChallengeRoutingType(str, Enum):
    MUNICIPALITY = "MUNICIPALITY"
    GOVERNMENT = "GOVERNMENT"
    INNOVATION = "INNOVATION"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    
class ChallengeLocationSource(str, Enum):
    MANUAL = "MANUAL"
    GPS = "GPS"
    GPS_VERIFIED_MANUAL = "GPS_VERIFIED_MANUAL"
    CONFLICT = "CONFLICT"


class Challenge(Base):
    __tablename__ = "challenges"

    # ========================================================
    # Primary Key
    # ========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # ========================================================
    # Basic Challenge Information
    # ========================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    submitted_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    is_anonymous: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    upvotes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ========================================================
    # Classification
    # ========================================================

    category: Mapped[ChallengeCategory] = mapped_column(
        SQLEnum(ChallengeCategory),
        default=ChallengeCategory.OTHER,
        nullable=False,
        index=True,
    )

    severity: Mapped[ChallengeSeverity] = mapped_column(
        SQLEnum(ChallengeSeverity),
        default=ChallengeSeverity.MEDIUM,
        nullable=False,
        index=True,
    )

    urgency: Mapped[ChallengeUrgency] = mapped_column(
        SQLEnum(ChallengeUrgency),
        default=ChallengeUrgency.MEDIUM,
        nullable=False,
        index=True,
    )

    # ========================================================
    # Impact / Location
    # ========================================================

    affected_population: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    estimated_economic_loss: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ========================================================
    # Location Resolution
    # ========================================================

    location_source: Mapped[ChallengeLocationSource] = mapped_column(
        SQLEnum(ChallengeLocationSource),
        default=ChallengeLocationSource.MANUAL,nullable=False,
        index=True,
    )

    location_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    location_accuracy_meters: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    locality: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    location_resolution_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location_resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # ========================================================
    # AI / Innovation Assessment
    # ========================================================

    innovation_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # Innovation-required model evidence
    # --------------------------------------------------------

    ai_innovation_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_innovation_decision: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ai_innovation_requires_human_review: Mapped[bool | None] = (
        mapped_column(
            Boolean,
            nullable=True,
        )
    )

    # --------------------------------------------------------
    # Innovation-type model evidence
    # --------------------------------------------------------

    ai_innovation_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_innovation_type_confidence: Mapped[float | None] = (
        mapped_column(
            Float,
            nullable=True,
        )
    )

    ai_innovation_type_second: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_innovation_type_second_confidence: Mapped[
        float | None
    ] = mapped_column(
        Float,
        nullable=True,
    )

    ai_innovation_type_margin: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_innovation_type_decision: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ai_innovation_type_requires_human_review: Mapped[
        bool | None
    ] = mapped_column(
        Boolean,
        nullable=True,
    )

    ai_innovation_type_top_3: Mapped[
        list[dict] | None
    ] = mapped_column(
        JSON,
        nullable=True,
    )

    # --------------------------------------------------------
    # General AI evidence
    # --------------------------------------------------------

    ai_confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_model_version: Mapped[str | None] = mapped_column(
        String(225),
        nullable=True,
    )

    # --------------------------------------------------------
    # Category-model evidence
    # --------------------------------------------------------

    ai_category_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_second_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_second_category_confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_category_margin: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    ai_category_decision: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ai_requires_human_review: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    ai_category_top_3: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    ai_analysis_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ========================================================
    # Routing
    # ========================================================

    routing_type: Mapped[ChallengeRoutingType] = mapped_column(
        SQLEnum(ChallengeRoutingType),
        default=ChallengeRoutingType.HUMAN_REVIEW,
        nullable=False,
        index=True,
    )

    routing_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ========================================================
    # Current Authority Assignment
    # ========================================================
    #
    # This stores WHO currently owns the challenge.
    #
    # Example:
    # Municipality
    #      ↓
    # District Authority
    #      ↓
    # State Department
    #
    # The AI only recommends the initial route.
    # The receiving authority can reassign/escalate later.

    current_authority_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    current_authority: Mapped["Organization | None"] = relationship(
        "Organization",
        foreign_keys=[current_authority_id],
    )

    # --------------------------------------------------------
    # Assignment metadata
    # --------------------------------------------------------

    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    assigned_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    assigned_by_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_by],
    )

    # ========================================================
    # Challenge Lifecycle
    # ========================================================

    status: Mapped[ChallengeStatus] = mapped_column(
        SQLEnum(ChallengeStatus),
        default=ChallengeStatus.SUBMITTED,
        nullable=False,
        index=True,
    )

    # ========================================================
    # Duplicate / Master Challenge
    # ========================================================

    is_master_challenge: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    master_challenge_id: Mapped[int | None] = mapped_column(
        ForeignKey("challenges.id"),
        nullable=True,
        index=True,
    )

    duplicate_similarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ========================================================
    # Evidence
    # ========================================================

    evidence: Mapped[list["ChallengeEvidence"]] = relationship(
        "ChallengeEvidence",
        back_populates="challenge",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # Timestamps
    # ========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            f"<Challenge("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status}', "
            f"category='{self.category}', "
            f"current_authority_id={self.current_authority_id}"
            f")>"
        )
    
    innovation_opportunity: Mapped[
        "InnovationOpportunity | None"
        ] = relationship(
            "InnovationOpportunity",
            back_populates="challenge",
            uselist=False,
        )