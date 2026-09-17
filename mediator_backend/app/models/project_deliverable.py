from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
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


class ProjectDeliverableStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    OVERDUE = "OVERDUE"


class ProjectDeliverable(Base):
    __tablename__ = "project_deliverables"
    
    __table_args__ = (
        Index(
            "ix_project_deliverables_status",
            "status",
        ),
    )

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

    milestone_id = Column(
        Integer,
        ForeignKey(
            "project_milestones.id",
            ondelete="CASCADE",
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

    due_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    approved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    status = Column(
        SQLEnum(
            ProjectDeliverableStatus,
            name="projectdeliverablestatus",
        ),
        nullable=False,
        default=ProjectDeliverableStatus.PENDING,
    )

    submission_reference = Column(
        Text,
        nullable=True,
    )

    review_remarks = Column(
        Text,
        nullable=True,
    )

    is_mandatory = Column(
        Boolean,
        nullable=False,
        default=True,
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
        back_populates="deliverables",
    )

    milestone = relationship(
        "ProjectMilestone",
        back_populates="deliverable_items",
    )