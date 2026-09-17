from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.database import Base

from app.models.proposal_evaluation import ProposalEvaluation

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
)

from app.models.project import Project
from app.models.project_milestone import ProjectMilestone
from app.models.project_deliverable import ProjectDeliverable
from app.models.project_funding import ProjectFundingTransaction
from app.models.project_report import ProjectReport
from app.models.project_evidence import ProjectEvidence
from app.models.project_outcome import ProjectOutcome
from app.models.project_risk import ProjectRisk
from app.models.notification import Notification
from app.models.reputation import ReputationEvent
from app.models.reputation_score import ReputationScore

# Import ALL models so they are registered with Base.metadata.
from app.models import (
    Challenge,
    ChallengeEvidence,
    InnovationOpportunity,
    Organization,
    OrganizationCapability,
    User,
    InnovationOpportunity,
    Organization,
    OrganizationCapability,
    RFP,
    RFPInvitation,
    UniversityProposal,
    ProposalEvaluation,
    User,
)

# ============================================================
# Alembic Configuration
# ============================================================

config = context.config


# ============================================================
# Logging
# ============================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ============================================================
# Database URL
# ============================================================

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)


# ============================================================
# Target Metadata
# ============================================================

target_metadata = Base.metadata


# ============================================================
# Alembic Object Filtering
# ============================================================

def include_object(
    object,
    name,
    type_,
    reflected,
    compare_to,
):
    """
    Control which database objects Alembic includes
    during autogenerate comparisons.

    The single SUPER_ADMIN index is intentionally managed
    by an explicit migration because it is a PostgreSQL
    partial/expression index and is not represented as a
    normal SQLAlchemy Index in the ORM model.
    """

    if (
        type_ == "index"
        and name == "uq_users_single_super_admin"
    ):
        return False

    return True


# ============================================================
# Offline Migration
# ============================================================

def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    """

    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# Online Migration
# ============================================================

def run_migrations_online() -> None:
    """
    Run migrations using a live database connection.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# Execute
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
