from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectReportType(str, Enum):
    PROGRESS = "PROGRESS"
    MILESTONE = "MILESTONE"
    FINANCIAL = "FINANCIAL"
    PILOT = "PILOT"
    FINAL = "FINAL"


class ProjectReportStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ProjectReport(Base):
    __tablename__ = "project_reports"

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
            ondelete="SET NULL",
        ),
        nullable=True,
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

    report_type = Column(
        SQLEnum(
            ProjectReportType,
            name="projectreporttype",
        ),
        nullable=False,
    )

    title = Column(
        Text,
        nullable=False,
    )

    summary = Column(
        Text,
        nullable=False,
    )

    findings = Column(
        Text,
        nullable=True,
    )

    challenges = Column(
        Text,
        nullable=True,
    )

    next_steps = Column(
        Text,
        nullable=True,
    )

    status = Column(
        SQLEnum(
            ProjectReportStatus,
            name="projectreportstatus",
        ),
        nullable=False,
        default=ProjectReportStatus.SUBMITTED,
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    review_remarks = Column(
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
        back_populates="reports",
    )

    milestone = relationship(
        "ProjectMilestone",
    )

    submitter = relationship(
        "User",
        foreign_keys=[submitted_by],
    )