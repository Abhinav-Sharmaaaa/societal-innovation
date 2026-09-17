from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProjectRiskStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"


class ProjectRisk(Base):
    __tablename__ = "project_risks"

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

    risk_level = Column(
        SQLEnum(
            ProjectRiskLevel,
            name="projectrisklevel",
        ),
        nullable=False,
    )

    risk_score = Column(
        Float,
        nullable=False,
    )

    title = Column(
        Text,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    detected_factors = Column(
        Text,
        nullable=True,
    )

    recommended_action = Column(
        Text,
        nullable=True,
    )

    status = Column(
        SQLEnum(
            ProjectRiskStatus,
            name="projectriskstatus",
        ),
        nullable=False,
        default=ProjectRiskStatus.OPEN,
    )

    detected_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    acknowledged_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolution_remarks = Column(
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
        back_populates="risks",
    )