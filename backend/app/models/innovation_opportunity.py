from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
    from app.models.challenge import Challenge
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.rfp import RFP


# ============================================================
# Innovation Opportunity Status
# ============================================================

class InnovationOpportunityStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    RFP_CREATED = "RFP_CREATED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


# ============================================================
# Innovation Opportunity
# ============================================================

class InnovationOpportunity(Base):
    __tablename__ = "innovation_opportunities"
    
    __table_args__ = (
            UniqueConstraint(
                "challenge_id",
                name="uq_innovation_opportunity_challenge",
            ),
        )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Source Challenge
    # --------------------------------------------------------

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey(
            "challenges.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    challenge: Mapped["Challenge"] = relationship(
        "Challenge",
        back_populates="innovation_opportunity",
    )

    # --------------------------------------------------------
    # Sponsoring Organization
    # --------------------------------------------------------

    sponsoring_organization_id: Mapped[int] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    sponsoring_organization: Mapped["Organization"] = relationship(
        "Organization",
    )

    # --------------------------------------------------------
    # Creation / Approval
    # --------------------------------------------------------

    created_by: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    approver: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approved_by],
    )

    # --------------------------------------------------------
    # Opportunity Information
    # --------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    problem_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    objectives: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    technical_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expected_outcomes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Planning / Constraints
    # --------------------------------------------------------

    estimated_budget: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    expected_duration_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    proposal_deadline: Mapped[object | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status: Mapped[InnovationOpportunityStatus] = mapped_column(
        SQLEnum(InnovationOpportunityStatus),
        nullable=False,
        default=InnovationOpportunityStatus.DRAFT,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    approved_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

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

    def __repr__(self) -> str:
        return (
            f"<InnovationOpportunity("
            f"id={self.id}, "
            f"challenge_id={self.challenge_id}, "
            f"title='{self.title}', "
            f"status='{self.status}'"
            f")>"
        )
    rfp: Mapped["RFP | None"] = relationship(
        "RFP",
        back_populates="innovation_opportunity",
        uselist=False,
    )
    