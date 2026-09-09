from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SQLEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


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
    # Location
    # --------------------------------------------------------

    district: Mapped[str | None] = mapped_column(
        String(100),
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
    # Representation
    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<Organization("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"type='{self.organization_type}'"
            f")>"
        )