from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectOutcomeStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class ProjectOutcomeMetricType(str, Enum):
    COUNT = "COUNT"
    PERCENTAGE = "PERCENTAGE"
    CURRENCY = "CURRENCY"
    SCORE = "SCORE"
    TEXT = "TEXT"


class ProjectOutcome(Base):
    __tablename__ = "project_outcomes"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    submitted_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    beneficiary_count = Column(
        Integer,
        nullable=True,
    )

    metric_name = Column(
        String(255),
        nullable=True,
    )

    metric_type = Column(
        SQLEnum(
            ProjectOutcomeMetricType,
            name="projectoutcomemetrictype",
        ),
        nullable=True,
    )

    baseline_value = Column(
        Float,
        nullable=True,
    )

    target_value = Column(
        Float,
        nullable=True,
    )

    achieved_value = Column(
        Float,
        nullable=True,
    )

    impact_score = Column(
        Float,
        nullable=True,
    )

    status = Column(
        SQLEnum(
            ProjectOutcomeStatus,
            name="projectoutcomestatus",
        ),
        nullable=False,
        default=ProjectOutcomeStatus.DRAFT,
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    verified_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    verification_remarks = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    project = relationship(
        "Project",
        back_populates="outcomes",
    )

    submitter = relationship(
        "User",
        foreign_keys=[submitted_by],
    )