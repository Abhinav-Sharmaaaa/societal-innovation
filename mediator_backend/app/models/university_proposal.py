from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.rfp import RFP
    from app.models.rfp_invitation import RFPInvitation
    from app.models.user import User


class UniversityProposalStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_EVALUATION = "UNDER_EVALUATION"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class UniversityProposal(Base):
    __tablename__ = "university_proposals"
    
    __table_args__ = (
        UniqueConstraint(
            "invitation_id",
            name="uq_university_proposal_invitation",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    rfp_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rfps.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    rfp: Mapped["RFP"] = relationship(
        "RFP",
        back_populates="proposals",
    )

    invitation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rfp_invitations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    invitation: Mapped["RFPInvitation"] = relationship(
        "RFPInvitation",
        back_populates="proposal",
    )

    university_id: Mapped[int] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    university: Mapped["Organization"] = relationship(
        "Organization",
    )

    submitted_by: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    submitter: Mapped["User"] = relationship(
        "User",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    solution: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    technical_approach: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    research_methodology: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    required_resources: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estimated_cost: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    expected_timeline_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    faculty_team: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expected_outcomes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    technology_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[UniversityProposalStatus] = mapped_column(
        SQLEnum(UniversityProposalStatus),
        nullable=False,
        default=UniversityProposalStatus.DRAFT,
        index=True,
    )

    submitted_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    evaluation = relationship(
        "ProposalEvaluation",
        back_populates="proposal",
        uselist=False,
        cascade="all, delete-orphan",
    )
    
    industry_collaboration_proposals = relationship(
        "IndustryCollaborationProposal",
        back_populates="university_proposal",
        cascade="all, delete-orphan",
    )