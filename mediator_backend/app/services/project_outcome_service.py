from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_outcome import (
    ProjectOutcome,
    ProjectOutcomeMetricType,
    ProjectOutcomeStatus,
)
from app.models.reputation import ReputationEventType
from app.models.user import User, UserRole
from app.schemas.project_outcome import (
    ProjectOutcomeCreate,
    ProjectOutcomeVerification,
)
from app.services.reputation_service import award_reputation_points


GOVERNMENT_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.GOVERNMENT_OFFICER,
    UserRole.MUNICIPALITY_OFFICER,
}

PARTNER_ROLES = {
    UserRole.UNIVERSITY_ADMIN,
    UserRole.FACULTY,
    UserRole.INDUSTRY_ADMIN,
    UserRole.INDUSTRY_MEMBER,
}


def _get_project(
    db: Session,
    project_id: int,
) -> Project:

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


def _check_project_access(
    project: Project,
    current_user: User,
) -> None:

    if current_user.role == UserRole.SUPER_ADMIN:
        return

    if current_user.role in {
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        if current_user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Government user is not associated "
                    "with an organization."
                ),
            )
        return

    if current_user.role in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        if current_user.organization_id != project.university_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized for this project.",
            )
        return

    if current_user.role in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        if current_user.organization_id != project.industry_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized for this project.",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized for this project.",
    )


def _validate_metric_values(
    outcome_data: ProjectOutcomeCreate,
) -> None:

    metric_type = outcome_data.metric_type

    if metric_type == "TEXT":
        return

    if metric_type is not None:
        if outcome_data.target_value is not None:
            if outcome_data.baseline_value is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Baseline value is required when "
                        "a target value is provided."
                    ),
                )

    if (
        outcome_data.baseline_value is not None
        and outcome_data.target_value is not None
        and outcome_data.target_value < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target value cannot be negative.",
        )


def create_project_outcome(
    db: Session,
    outcome_data: ProjectOutcomeCreate,
    current_user: User,
) -> ProjectOutcome:

    project = _get_project(
        db,
        outcome_data.project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    if current_user.role not in PARTNER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only university or industry project "
                "partners can submit outcomes."
            ),
        )

    _validate_metric_values(
        outcome_data
    )

    outcome = ProjectOutcome(
        project_id=project.id,
        submitted_by=current_user.id,

        title=outcome_data.title,
        description=outcome_data.description,

        beneficiary_count=(
            outcome_data.beneficiary_count
        ),

        metric_name=outcome_data.metric_name,

        metric_type=(
            ProjectOutcomeMetricType(
                outcome_data.metric_type
            )
            if outcome_data.metric_type
            else None
        ),

        baseline_value=(
            outcome_data.baseline_value
        ),
        target_value=(
            outcome_data.target_value
        ),
        achieved_value=(
            outcome_data.achieved_value
        ),

        impact_score=(
            outcome_data.impact_score
        ),

        status=ProjectOutcomeStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
    )

    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    return outcome


def verify_project_outcome(
    db: Session,
    outcome_id: int,
    verification_data: ProjectOutcomeVerification,
    current_user: User,
) -> ProjectOutcome:

    if current_user.role not in GOVERNMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users "
                "can verify project outcomes."
            ),
        )

    outcome = (
        db.query(ProjectOutcome)
        .filter(
            ProjectOutcome.id == outcome_id
        )
        .first()
    )

    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project outcome not found.",
        )

    project = outcome.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if outcome.status not in {
        ProjectOutcomeStatus.SUBMITTED,
        ProjectOutcomeStatus.UNDER_REVIEW,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This outcome cannot be verified "
                "in its current state."
            ),
        )

    # ---------------------------------------------------------
    # Determine final verification decision
    # ---------------------------------------------------------
    verification_status = ProjectOutcomeStatus(
        verification_data.decision
    )

    outcome.status = verification_status

    outcome.verified_at = datetime.now(
        timezone.utc
    )

    outcome.verification_remarks = (
        verification_data.verification_remarks
    )

    # ---------------------------------------------------------
    # Persist verification result
    # ---------------------------------------------------------
    db.commit()
    db.refresh(outcome)

    # ---------------------------------------------------------
    # Reputation:
    #
    # VERIFIED outcome -> +75 to university
    # VERIFIED outcome -> +75 to industry
    #
    # The outcome ID is part of the event description,
    # making the reward idempotent.
    # ---------------------------------------------------------
    if (
        verification_status
        == ProjectOutcomeStatus.VERIFIED
    ):

        # University +75
        if project.university_id is not None:

            award_reputation_points(
                db=db,
                event_type=(
                    ReputationEventType.POSITIVE_PROJECT_OUTCOME
                ),
                description=(
                    f"Positive project outcome verified: "
                    f"outcome_id={outcome.id}:university"
                ),
                organization_id=project.university_id,
                project_id=project.id,
            )

        # Industry +75
        if project.industry_id is not None:

            award_reputation_points(
                db=db,
                event_type=(
                    ReputationEventType.POSITIVE_PROJECT_OUTCOME
                ),
                description=(
                    f"Positive project outcome verified: "
                    f"outcome_id={outcome.id}:industry"
                ),
                organization_id=project.industry_id,
                project_id=project.id,
            )

        db.refresh(outcome)

    return outcome


def list_project_outcomes(
    db: Session,
    project_id: int,
    current_user: User,
) -> list[ProjectOutcome]:

    project = _get_project(
        db,
        project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    return (
        db.query(ProjectOutcome)
        .filter(
            ProjectOutcome.project_id == project_id
        )
        .order_by(
            ProjectOutcome.created_at.desc()
        )
        .all()
    )