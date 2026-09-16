from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import (
    Project,
    ProjectHealth,
    ProjectStatus,
)
from app.models.project_milestone import (
    ProjectMilestone,
    ProjectMilestoneStatus,
)
from app.models.reputation import ReputationEventType
from app.models.user import User, UserRole
from app.schemas.project_milestone import (
    ProjectMilestoneUpdate,
)
from app.services.reputation_service import award_reputation_points


def update_milestone(
    db: Session,
    milestone_id: int,
    milestone_data: ProjectMilestoneUpdate,
    current_user: User,
) -> ProjectMilestone:

    # ---------------------------------------------------------
    # 1. Load milestone
    # ---------------------------------------------------------
    milestone = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.id == milestone_id
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

    # ---------------------------------------------------------
    # 2. Authorization
    # ---------------------------------------------------------
    if current_user.role == UserRole.SUPER_ADMIN:
        pass

    elif current_user.role in {
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

        # Detailed jurisdiction checks can be tightened later.

    elif current_user.role in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        if current_user.organization_id != project.university_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized to update milestones "
                    "for this university project."
                ),
            )

    elif current_user.role in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        if current_user.organization_id != project.industry_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized to update milestones "
                    "for this industry project."
                ),
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to update "
                "project milestones."
            ),
        )

    # ---------------------------------------------------------
    # 3. Validate project state
    # ---------------------------------------------------------
    if project.status in {
        ProjectStatus.COMPLETED,
        ProjectStatus.CANCELLED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Milestones cannot be updated for a completed "
                "or cancelled project."
            ),
        )

    # ---------------------------------------------------------
    # 4. Remember previous milestone state
    #
    # Used to detect a genuine transition into COMPLETED.
    # ---------------------------------------------------------
    previous_status = milestone.status

    # ---------------------------------------------------------
    # 5. Update milestone
    # ---------------------------------------------------------
    milestone.progress_percentage = (
        milestone_data.progress_percentage
    )

    milestone.status = ProjectMilestoneStatus(
        milestone_data.status
    )

    if milestone_data.completion_remarks is not None:
        milestone.completion_remarks = (
            milestone_data.completion_remarks
        )

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 6. Handle completion
    # ---------------------------------------------------------
    milestone_completed_now = (
        milestone.status == ProjectMilestoneStatus.COMPLETED
        and previous_status
        != ProjectMilestoneStatus.COMPLETED
    )

    if (
        milestone.status
        == ProjectMilestoneStatus.COMPLETED
    ):
        milestone.progress_percentage = 100

        if milestone.completed_at is None:
            milestone.completed_at = now

    else:
        milestone.completed_at = None

    # ---------------------------------------------------------
    # 7. Detect overdue milestone
    # ---------------------------------------------------------
    if (
        milestone.due_date is not None
        and milestone.due_date < now
        and milestone.status
        != ProjectMilestoneStatus.COMPLETED
    ):
        milestone.status = ProjectMilestoneStatus.DELAYED

    # ---------------------------------------------------------
    # 8. Recalculate project progress
    # ---------------------------------------------------------
    milestones = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.project_id
            == project.id
        )
        .all()
    )

    if milestones:
        project.progress_percentage = round(
            sum(
                m.progress_percentage
                for m in milestones
            )
            / len(milestones),
            2,
        )
    else:
        project.progress_percentage = 0

    # ---------------------------------------------------------
    # 9. Recalculate project health
    # ---------------------------------------------------------
    delayed_count = sum(
        1
        for m in milestones
        if m.status
        == ProjectMilestoneStatus.DELAYED
    )

    blocked_count = sum(
        1
        for m in milestones
        if m.status
        == ProjectMilestoneStatus.BLOCKED
    )

    if blocked_count > 0:
        project.health = ProjectHealth.CRITICAL

    elif delayed_count >= 2:
        project.health = ProjectHealth.DELAYED

    elif delayed_count == 1:
        project.health = ProjectHealth.AT_RISK

    else:
        project.health = ProjectHealth.ON_TRACK

    # ---------------------------------------------------------
    # 10. Activate project once execution begins
    # ---------------------------------------------------------
    if (
        project.status == ProjectStatus.PLANNING
        and milestone.progress_percentage > 0
    ):
        project.status = ProjectStatus.ACTIVE

    # ---------------------------------------------------------
    # 11. Automatically complete project
    #
    # IMPORTANT:
    # Initialize project_was_completed before the condition
    # so it is always defined when checked later.
    # ---------------------------------------------------------
    project_was_completed = False

    all_completed = (
        bool(milestones)
        and all(
            m.status
            == ProjectMilestoneStatus.COMPLETED
            for m in milestones
        )
    )

    if all_completed:
        project_was_completed = (
            project.status != ProjectStatus.COMPLETED
        )

        project.status = ProjectStatus.COMPLETED
        project.health = ProjectHealth.ON_TRACK
        project.progress_percentage = 100

        if project.actual_completion_date is None:
            project.actual_completion_date = now

    # ---------------------------------------------------------
    # 12. Project completion reputation
    #
    # Award only when the project transitions into
    # COMPLETED. This prevents repeated +50 awards.
    # ---------------------------------------------------------
    if project_was_completed:

        # University +50
        award_reputation_points(
            db=db,
            event_type=(
                ReputationEventType.PROJECT_COMPLETED
            ),
            description=(
                f"Project completed: "
                f"project_id={project.id}:university"
            ),
            organization_id=project.university_id,
            project_id=project.id,
        )

        # Industry +50
        if project.industry_id is not None:
            award_reputation_points(
                db=db,
                event_type=(
                    ReputationEventType.PROJECT_COMPLETED
                ),
                description=(
                    f"Project completed: "
                    f"project_id={project.id}:industry"
                ),
                organization_id=project.industry_id,
                project_id=project.id,
            )

    # ---------------------------------------------------------
    # 13. Award university reputation
    #
    # A university receives +10 when a milestone transitions
    # into COMPLETED.
    #
    # The description contains the milestone ID so the
    # reputation service can prevent duplicate awards.
    # ---------------------------------------------------------
    if milestone_completed_now:

        award_reputation_points(
            db=db,
            event_type=(
                ReputationEventType.MILESTONE_COMPLETED
            ),
            description=(
                f"Milestone completed: "
                f"milestone_id={milestone.id}"
            ),
            organization_id=project.university_id,
            project_id=project.id,
        )

    else:
        # No reputation event was created, so we still need
        # to persist the milestone/project changes.
        db.commit()

    db.refresh(milestone)

    return milestone


def list_project_milestones(
    db: Session,
    project_id: int,
    current_user: User,
) -> list[ProjectMilestone]:

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

    # ---------------------------------------------------------
    # Authorization
    # ---------------------------------------------------------
    if current_user.role == UserRole.SUPER_ADMIN:
        pass

    elif current_user.role in {
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

    elif current_user.role in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        if current_user.organization_id != project.university_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized to view this project."
                ),
            )

    elif current_user.role in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        if current_user.organization_id != project.industry_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not authorized to view this project."
                ),
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to view "
                "project milestones."
            ),
        )

    return (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.project_id == project_id
        )
        .order_by(
            ProjectMilestone.sequence_number
        )
        .all()
    )