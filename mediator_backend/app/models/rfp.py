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
    from app.models.innovation_opportunity import InnovationOpportunity
    from app.models.user import User
    from app.models.rfp_invitation import RFPInvitation
    from app.models.university_proposal import UniversityProposal


# ============================================================
# RFP Status
# ============================================================

class RFPStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


# ============================================================
# RFP Model
# ============================================================

class RFP(Base):
    __tablename__ = "rfps"
    
    __table_args__ = (
        UniqueConstraint(
            "innovation_opportunity_id",
            name="uq_rfps_innovation_opportunity",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Source Innovation Opportunity
    # --------------------------------------------------------

    innovation_opportunity_id: Mapped[int] = mapped_column(
        ForeignKey(
            "innovation_opportunities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    innovation_opportunity: Mapped[
        "InnovationOpportunity"
    ] = relationship(
        "InnovationOpportunity",
        back_populates="rfp",
    )

    # --------------------------------------------------------
    # Creation
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

    # --------------------------------------------------------
    # RFP Information
    # --------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
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

    status: Mapped[RFPStatus] = mapped_column(
        SQLEnum(RFPStatus),
        nullable=False,
        default=RFPStatus.DRAFT,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    published_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[object | None] = mapped_column(
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
            f"<RFP("
            f"id={self.id}, "
            f"innovation_opportunity_id="
            f"{self.innovation_opportunity_id}, "
            f"title='{self.title}', "
            f"status='{self.status}'"
            f")>"
        )
        
    invitations: Mapped[list["RFPInvitation"]] = relationship(
        "RFPInvitation",
        back_populates="rfp",
        cascade="all, delete-orphan",
    )
    proposals: Mapped[list["UniversityProposal"]] = relationship(
        "UniversityProposal",
        back_populates="rfp",
        cascade="all, delete-orphan",
    )