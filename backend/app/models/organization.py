from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.organization_competency import OrganizationCompetency
    from app.models.organization_capability import OrganizationCapability


# ============================================================
# Organization Types
# ============================================================

class OrganizationType(str, Enum):
    MUNICIPALITY = "MUNICIPALITY"
    GOVERNMENT_DEPARTMENT = "GOVERNMENT_DEPARTMENT"
    UNIVERSITY = "UNIVERSITY"
    INDUSTRY = "INDUSTRY"


# ============================================================
# Organization Model
# ============================================================

class Organization(Base):
    __tablename__ = "organizations"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Organization Information
    # --------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    organization_type: Mapped[OrganizationType] = mapped_column(
        SQLEnum(OrganizationType),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    

    # --------------------------------------------------------
    # Hierarchy
    # --------------------------------------------------------
    # Allows organizations/authorities to be linked in a
    # parent-child structure.
    #
    # Example:
    #
    # State Disaster Management Authority
    #           ↓
    # District Disaster Management Authority
    #           ↓
    # Municipal Authority
    #
    # The same hierarchy mechanism also works for delegation
    # and reassignment.

    parent_organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    parent_organization: Mapped["Organization | None"] = relationship(
        "Organization",
        remote_side="Organization.id",
        back_populates="child_organizations",
    )

    child_organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        back_populates="parent_organization",
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    
    locality: Mapped[str | None] = mapped_column(
            String(255),
            nullable=True,
            index=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # --------------------------------------------------------
    # Contact Information
    # --------------------------------------------------------

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # --------------------------------------------------------
    # Users
    # --------------------------------------------------------

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
    )
    
        # --------------------------------------------------------
    # Competencies
    # --------------------------------------------------------

    competencies: Mapped[list["OrganizationCompetency"]] = relationship(
        "OrganizationCompetency",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    
    # --------------------------------------------------------
# Collaboration Capabilities
# --------------------------------------------------------

    capabilities: Mapped[list["OrganizationCapability"]] = relationship(
        "OrganizationCapability",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    # --------------------------------------------------------
    # Representation
    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Organization("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"type='{self.organization_type}', "
            f"parent_id={self.parent_organization_id}"
            f")>"
        )