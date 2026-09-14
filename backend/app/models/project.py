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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProjectHealth(str, Enum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    DELAYED = "DELAYED"
    CRITICAL = "CRITICAL"


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    collaboration_id = Column(
        Integer,
        ForeignKey(
            "industry_collaboration_proposals.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    challenge_id = Column(
        Integer,
        ForeignKey(
            "challenges.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    university_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    industry_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    created_by = Column(
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
        nullable=True,
    )

    objectives = Column(
        Text,
        nullable=True,
    )

    expected_outcomes = Column(
        Text,
        nullable=True,
    )

    total_budget = Column(
        Float,
        nullable=True,
    )

    start_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    target_completion_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    actual_completion_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    status = Column(
        SQLEnum(
            ProjectStatus,
            name="projectstatus",
        ),
        nullable=False,
        default=ProjectStatus.PLANNING,
    )

    health = Column(
        SQLEnum(
            ProjectHealth,
            name="projecthealth",
        ),
        nullable=False,
        default=ProjectHealth.ON_TRACK,
    )

    progress_percentage = Column(
        Float,
        nullable=False,
        default=0,
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

    collaboration = relationship(
        "IndustryCollaborationProposal",
        back_populates="project",
        uselist=False,
    )

    university = relationship(
        "Organization",
        foreign_keys=[university_id],
    )

    industry = relationship(
        "Organization",
        foreign_keys=[industry_id],
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
    )

    __table_args__ = (
        UniqueConstraint(
            "collaboration_id",
            name="uq_project_collaboration",
        ),
    )
    
    milestones = relationship(
        "ProjectMilestone",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMilestone.sequence_number",
    )
    
    deliverables = relationship(
        "ProjectDeliverable",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    funding_transactions = relationship(
        "ProjectFundingTransaction",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    reports = relationship(
        "ProjectReport",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    evidence = relationship(
        "ProjectEvidence",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    outcomes = relationship(
        "ProjectOutcome",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    risks = relationship(
        "ProjectRisk",
        back_populates="project",
        cascade="all, delete-orphan",
    )