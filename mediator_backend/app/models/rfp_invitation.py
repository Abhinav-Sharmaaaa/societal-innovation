from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Float,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.rfp import RFP
    from app.models.user import User
    from app.models.university_proposal import UniversityProposal


class RFPInvitationStatus(str, Enum):
    INVITED = "INVITED"
    VIEWED = "VIEWED"
    INTERESTED = "INTERESTED"
    DECLINED = "DECLINED"
    PROPOSAL_SUBMITTED = "PROPOSAL_SUBMITTED"
    EXPIRED = "EXPIRED"


class RFPInvitation(Base):
    __tablename__ = "rfp_invitations"

    __table_args__ = (
        UniqueConstraint(
            "rfp_id",
            "university_id",
            name="uq_rfp_invitation_university",
        ),
    )
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # RFP
    # --------------------------------------------------------

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
        back_populates="invitations",
    )

    # --------------------------------------------------------
    # Invited University
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Government action
    # --------------------------------------------------------

    invited_by: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    inviter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_by],
    )

    # --------------------------------------------------------
    # AI recommendation metadata
    # --------------------------------------------------------

    recommendation_rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    match_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # --------------------------------------------------------
    # Status / response
    # --------------------------------------------------------

    status: Mapped[RFPInvitationStatus] = mapped_column(
        SQLEnum(RFPInvitationStatus),
        nullable=False,
        default=RFPInvitationStatus.INVITED,
        index=True,
    )

    response_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    invited_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    viewed_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    responded_at: Mapped[object | None] = mapped_column(
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
    
    proposal: Mapped["UniversityProposal | None"] = relationship(
        "UniversityProposal",
        back_populates="invitation",
        uselist=False,
    )

    def __repr__(self) -> str:
        return (
            f"<RFPInvitation("
            f"id={self.id}, "
            f"rfp_id={self.rfp_id}, "
            f"university_id={self.university_id}, "
            f"status='{self.status}'"
            f")>"
        )