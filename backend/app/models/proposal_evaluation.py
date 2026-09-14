from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProposalEvaluationDecision(str, Enum):
    UNDER_REVIEW = "UNDER_REVIEW"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"


class ProposalEvaluation(Base):
    __tablename__ = "proposal_evaluations"

    id = Column(Integer, primary_key=True)

    proposal_id = Column(
        Integer,
        ForeignKey(
            "university_proposals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    evaluated_by = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # Evaluation criteria
    technical_feasibility_score = Column(
        Float,
        nullable=False,
    )

    innovation_score = Column(
        Float,
        nullable=False,
    )

    cost_effectiveness_score = Column(
        Float,
        nullable=False,
    )

    impact_score = Column(
        Float,
        nullable=False,
    )

    timeline_score = Column(
        Float,
        nullable=False,
    )

    scalability_score = Column(
        Float,
        nullable=False,
    )

    research_capability_score = Column(
        Float,
        nullable=False,
    )

    # Calculated overall score
    overall_score = Column(
        Float,
        nullable=False,
    )

    remarks = Column(
        Text,
        nullable=True,
    )

    decision = Column(
        SQLEnum(
            ProposalEvaluationDecision,
            name="proposalevaluationdecision",
        ),
        nullable=False,
        default=ProposalEvaluationDecision.UNDER_REVIEW,
    )

    evaluated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
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

    proposal = relationship(
        "UniversityProposal",
        back_populates="evaluation",
    )

    evaluator = relationship(
        "User",
    )

    __table_args__ = (
        UniqueConstraint(
            "proposal_id",
            name="uq_proposal_evaluation_proposal",
        ),
    )