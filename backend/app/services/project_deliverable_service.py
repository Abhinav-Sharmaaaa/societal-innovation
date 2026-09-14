from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_deliverable import (
    ProjectDeliverable,
    ProjectDeliverableStatus,
)
from app.models.project_milestone import ProjectMilestone
from app.models.reputation import ReputationEventType
from app.models.user import User, UserRole
from app.schemas.project_deliverable import (
    ProjectDeliverableCreate,
    ProjectDeliverableReview,
    ProjectDeliverableSubmit,
)
from app.services.reputation_service import award_reputation_points


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
                detail=(
                    "You are not authorized for this "
                    "university project."
                ),
            )
        return

    if current_user.role in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        if current_user.organization_id != project.industry_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized for this "
                    "industry project."
                ),
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to access this project.",
    )


def create_deliverable(
    db: Session,
    deliverable_data: ProjectDeliverableCreate,
    current_user: User,
) -> ProjectDeliverable:

    milestone = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.id
            == deliverable_data.milestone_id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project milestone not found.",
        )

    project = milestone.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if project.status.value in {
        "COMPLETED",
        "CANCELLED",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot create deliverables for a completed "
                "or cancelled project."
            ),
        )

    due_date = deliverable_data.due_date

    if due_date is not None:
        if due_date.tzinfo is None:
            due_date = due_date.replace(
                tzinfo=timezone.utc
            )

        if due_date < milestone.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Deliverable due date cannot be before "
                    "the milestone start date."
                ),
            )

        if (
            milestone.due_date is not None
            and due_date > milestone.due_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Deliverable due date cannot exceed "
                    "the milestone due date."
                ),
            )

    deliverable = ProjectDeliverable(
        project_id=project.id,
        milestone_id=milestone.id,
        title=deliverable_data.title,
        description=deliverable_data.description,
        due_date=due_date,
        status=ProjectDeliverableStatus.PENDING,
        is_mandatory=deliverable_data.is_mandatory,
    )

    db.add(deliverable)
    db.commit()
    db.refresh(deliverable)

    return deliverable


def submit_deliverable(
    db: Session,
    deliverable_id: int,
    submission_data: ProjectDeliverableSubmit,
    current_user: User,
) -> ProjectDeliverable:

    deliverable = (
        db.query(ProjectDeliverable)
        .filter(
            ProjectDeliverable.id == deliverable_id
        )
        .first()
    )

    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project deliverable not found.",
        )

    project = deliverable.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if current_user.role not in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only project university or industry members "
                "can submit deliverables."
            ),
        )

    if deliverable.status not in {
        ProjectDeliverableStatus.PENDING,
        ProjectDeliverableStatus.IN_PROGRESS,
        ProjectDeliverableStatus.REJECTED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "This deliverable cannot be submitted "
                "in its current state."
            ),
        )

    now = datetime.now(timezone.utc)

    deliverable.submission_reference = (
        submission_data.submission_reference
    )
    deliverable.submitted_at = now
    deliverable.status = ProjectDeliverableStatus.SUBMITTED

    if (
        deliverable.due_date is not None
        and now > deliverable.due_date
    ):
        deliverable.status = ProjectDeliverableStatus.OVERDUE

    db.commit()
    db.refresh(deliverable)

    return deliverable


def review_deliverable(
    db: Session,
    deliverable_id: int,
    review_data: ProjectDeliverableReview,
    current_user: User,
) -> ProjectDeliverable:

    deliverable = (
        db.query(ProjectDeliverable)
        .filter(
            ProjectDeliverable.id == deliverable_id
        )
        .first()
    )

    if not deliverable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project deliverable not found.",
        )

    project = deliverable.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if current_user.role not in {
        UserRole.SUPER_ADMIN,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users "
                "can review deliverables."
            ),
        )

    if deliverable.status not in {
        ProjectDeliverableStatus.SUBMITTED,
        ProjectDeliverableStatus.OVERDUE,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted deliverables can be reviewed.",
        )

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # Capture decision
    # ---------------------------------------------------------
    approved = review_data.decision == "APPROVED"

    # ---------------------------------------------------------
    # Approve / reject deliverable
    # ---------------------------------------------------------
    if approved:
        deliverable.status = ProjectDeliverableStatus.APPROVED
        deliverable.approved_at = now

    else:
        deliverable.status = ProjectDeliverableStatus.REJECTED
        deliverable.approved_at = None

    deliverable.review_remarks = (
        review_data.review_remarks
    )

    # ---------------------------------------------------------
    # Persist deliverable decision first
    # ---------------------------------------------------------
    db.commit()
    db.refresh(deliverable)

    # ---------------------------------------------------------
    # Reputation:
    # Approved deliverable -> University +10
    #
    # Description contains the deliverable ID so the
    # reputation service can prevent duplicate awards.
    # ---------------------------------------------------------
    if approved:
        award_reputation_points(
            db=db,
            event_type=(
                ReputationEventType.DELIVERABLE_APPROVED
            ),
            description=(
                f"Deliverable approved: "
                f"deliverable_id={deliverable.id}"
            ),
            organization_id=project.university_id,
            project_id=project.id,
        )

        # award_reputation_points() commits its own transaction.
        db.refresh(deliverable)

    return deliverable