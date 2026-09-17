from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectEvidenceType(str, Enum):
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DATASET = "DATASET"
    LINK = "LINK"


class ProjectEvidence(Base):
    __tablename__ = "project_evidence"

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

    report_id = Column(
        Integer,
        ForeignKey(
            "project_reports.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    evidence_type = Column(
        SQLEnum(
            ProjectEvidenceType,
            name="projectevidencetype",
        ),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    file_url = Column(
        Text,
        nullable=True,
    )

    external_url = Column(
        Text,
        nullable=True,
    )

    description = Column(
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
        back_populates="evidence",
    )

    report = relationship(
        "ProjectReport",
    )

    uploader = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )