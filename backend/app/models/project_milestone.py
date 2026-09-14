from enum import Enum

from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectMilestoneStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    BLOCKED = "BLOCKED"


class ProjectMilestoneType(str, Enum):
    PROBLEM_VALIDATION = "PROBLEM_VALIDATION"
    RESEARCH_PLANNING = "RESEARCH_PLANNING"
    PROTOTYPE_DEVELOPMENT = "PROTOTYPE_DEVELOPMENT"
    TESTING_VALIDATION = "TESTING_VALIDATION"
    PILOT_DEPLOYMENT = "PILOT_DEPLOYMENT"
    FINAL_SOLUTION_DEPLOYMENT = "FINAL_SOLUTION_DEPLOYMENT"


class ProjectMilestone(Base):
    __tablename__ = "project_milestones"

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

    milestone_type = Column(
        SQLEnum(
            ProjectMilestoneType,
            name="projectmilestonetype",
        ),
        nullable=False,
    )

    sequence_number = Column(
        Integer,
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    deliverables = Column(
        Text,
        nullable=True,
    )

    start_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    due_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    status = Column(
        SQLEnum(
            ProjectMilestoneStatus,
            name="projectmilestonestatus",
        ),
        nullable=False,
        default=ProjectMilestoneStatus.NOT_STARTED,
    )

    progress_percentage = Column(
        Float,
        nullable=False,
        default=0,
    )

    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    completion_remarks = Column(
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
        back_populates="milestones",
    )
    
    deliverable_items = relationship(
        "ProjectDeliverable",
        back_populates="milestone",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_project_milestones_project_sequence",
            "project_id",
            "sequence_number",
        ),
        Index(
            "ix_project_milestones_status",
            "status",
        ),
    )