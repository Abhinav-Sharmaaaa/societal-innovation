from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class IndustryCollaborationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    MODIFICATION_REQUESTED = "MODIFICATION_REQUESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class IndustryCollaborationProposal(Base):
    __tablename__ = "industry_collaboration_proposals"

    id = Column(Integer, primary_key=True)

    # The shortlisted university proposal
    university_proposal_id = Column(
        Integer,
        ForeignKey(
            "university_proposals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Industry organization making the offer
    industry_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # Industry user who submits it
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
        Text,
        nullable=False,
    )

    collaboration_description = Column(
        Text,
        nullable=False,
    )

    # Financial contribution
    funding_amount = Column(
        Float,
        nullable=True,
    )

    # Technical support
    technical_mentorship = Column(
        Text,
        nullable=True,
    )

    industry_experts = Column(
        Text,
        nullable=True,
    )

    infrastructure_resources = Column(
        Text,
        nullable=True,
    )

    technology_support = Column(
        Text,
        nullable=True,
    )

    internship_support = Column(
        Text,
        nullable=True,
    )

    pilot_deployment_support = Column(
        Text,
        nullable=True,
    )

    commercialization_support = Column(
        Text,
        nullable=True,
    )

    proposed_duration_days = Column(
        Integer,
        nullable=True,
    )
    
    response_deadline = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    additional_terms = Column(
        Text,
        nullable=True,
    )

    status = Column(
        SQLEnum(
            IndustryCollaborationStatus,
            name="industrycollaborationstatus",
        ),
        nullable=False,
        default=IndustryCollaborationStatus.SUBMITTED,
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    reviewed_at = Column(
        DateTime(timezone=True),
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

    university_proposal = relationship(
        "UniversityProposal",
        back_populates="industry_collaboration_proposals",
    )
    
    project = relationship(
        "Project",
        back_populates="collaboration",
        uselist=False,
    )

    industry = relationship(
        "Organization",
    )

    submitter = relationship(
        "User",
    )

    __table_args__ = (
        UniqueConstraint(
            "university_proposal_id",
            "industry_id",
            name="uq_industry_collaboration_proposal",
        ),
    )