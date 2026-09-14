from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.challenge import ChallengeCategory

if TYPE_CHECKING:
    from app.models.organization import Organization


class OrganizationCompetency(Base):
    __tablename__ = "organization_competencies"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "category",
            name="uq_organization_competency",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    category: Mapped[ChallengeCategory] = mapped_column(
        SQLEnum(
            ChallengeCategory,
            name="challengecategory",
        ),
        nullable=False,
        index=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="competencies",
    )