from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ============================================================
# User Roles
# ============================================================

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"

    CITIZEN = "CITIZEN"

    MUNICIPALITY_OFFICER = "MUNICIPALITY_OFFICER"

    GOVERNMENT_OFFICER = "GOVERNMENT_OFFICER"

    UNIVERSITY_ADMIN = "UNIVERSITY_ADMIN"

    FACULTY = "FACULTY"

    STUDENT = "STUDENT"

    INDUSTRY_ADMIN = "INDUSTRY_ADMIN"

    INDUSTRY_MEMBER = "INDUSTRY_MEMBER"


# ============================================================
# User Model
# ============================================================

class User(Base):
    __tablename__ = "users"

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Basic Information
    # --------------------------------------------------------

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # --------------------------------------------------------
    # Role
    # --------------------------------------------------------

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # Organization
    # --------------------------------------------------------
    # Citizens normally have no organization.
    #
    # Officers, faculty, students and industry members can
    # belong to an organization.

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    organization: Mapped["Organization | None"] = relationship(
        "Organization",
        back_populates="users",
    )

    # --------------------------------------------------------
    # Account Status
    # --------------------------------------------------------

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Representation
    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"email='{self.email}', "
            f"role='{self.role}', "
            f"organization_id={self.organization_id}"
            f")>"
        )