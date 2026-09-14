from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization


class CapabilityType(str, Enum):
    UNIVERSITY_DISCIPLINE = "UNIVERSITY_DISCIPLINE"
    UNIVERSITY_RESEARCH_AREA = "UNIVERSITY_RESEARCH_AREA"
    UNIVERSITY_LAB = "UNIVERSITY_LAB"
    UNIVERSITY_EXPERTISE = "UNIVERSITY_EXPERTISE"

    INDUSTRY_TECHNOLOGY = "INDUSTRY_TECHNOLOGY"
    INDUSTRY_SERVICE = "INDUSTRY_SERVICE"
    INDUSTRY_MANUFACTURING = "INDUSTRY_MANUFACTURING"
    INDUSTRY_FUNDING = "INDUSTRY_FUNDING"
    INDUSTRY_DEPLOYMENT = "INDUSTRY_DEPLOYMENT"
    INDUSTRY_MENTORSHIP = "INDUSTRY_MENTORSHIP"


class OrganizationCapability(Base):
    __tablename__ = "organization_capabilities"

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

    capability_type: Mapped[CapabilityType] = mapped_column(
        SQLEnum(CapabilityType),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="capabilities",
    )

    def __repr__(self) -> str:
        return (
            f"<OrganizationCapability("
            f"id={self.id}, "
            f"organization_id={self.organization_id}, "
            f"type='{self.capability_type}', "
            f"name='{self.name}'"
            f")>"
        )