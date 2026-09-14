from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
    IndustryCollaborationStatus,
)
from app.models.notification import (
    Notification,
    NotificationPriority,
    NotificationType,
)
from app.models.project import Project
from app.models.project_deliverable import (
    ProjectDeliverable,
    ProjectDeliverableStatus,
)
from app.models.project_milestone import (
    ProjectMilestone,
    ProjectMilestoneStatus,
)
from app.models.rfp import (
    RFP,
    RFPStatus,
)
from app.models.rfp_invitation import (
    RFPInvitation,
    RFPInvitationStatus,
)
from app.models.user import User, UserRole


# ============================================================
# DEADLINE CONFIGURATION
# ============================================================

DEADLINE_THRESHOLDS = {
    7: NotificationPriority.MEDIUM,
    3: NotificationPriority.HIGH,
    1: NotificationPriority.HIGH,
    0: NotificationPriority.HIGH,
}

OVERDUE_PRIORITY = NotificationPriority.CRITICAL


# ============================================================
# HELPERS
# ============================================================

def _normalize_datetime(
    value: datetime,
) -> datetime:
    """
    Ensure datetime is timezone-aware.

    Database timestamps may occasionally arrive as naive
    values. Treat those as UTC.
    """

    if value.tzinfo is None:
        return value.replace(
            tzinfo=timezone.utc
        )

    return value


def _get_deadline_state(
    deadline: datetime,
    now: datetime,
) -> tuple[str, NotificationPriority] | None:
    """
    Determine whether a deadline is:

    - OVERDUE
    - DUE_TODAY
    - DUE_IN_7_DAYS
    - DUE_IN_3_DAYS
    - DUE_IN_1_DAYS

    Returns None when no alert should be generated yet.
    """

    deadline = _normalize_datetime(deadline)
    now = _normalize_datetime(now)

    # --------------------------------------------------------
    # Already overdue
    # --------------------------------------------------------

    if deadline < now:
        return (
            "OVERDUE",
            OVERDUE_PRIORITY,
        )

    # --------------------------------------------------------
    # Remaining time
    # --------------------------------------------------------

    remaining = deadline - now

    # `.days` gives completed 24-hour periods.
    days_remaining = remaining.days

    # Anything less than 24 hours from now is treated as
    # due today.
    if days_remaining <= 0:
        return (
            "DUE_TODAY",
            NotificationPriority.HIGH,
        )

    if days_remaining in DEADLINE_THRESHOLDS:
        return (
            f"DUE_IN_{days_remaining}_DAYS",
            DEADLINE_THRESHOLDS[days_remaining],
        )

    return None


def _notification_exists(
    db: Session,
    user_id: int,
    deadline_key: str,
    project_id: int | None = None,
) -> bool:
    """
    Check whether an unread notification already exists
    for this exact deadline state.

    Example deadline_key:

        RFP:15:DUE_IN_7_DAYS
        MILESTONE:21:OVERDUE
        DELIVERABLE:7:DUE_TODAY
    """

    query = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.notification_type
            == NotificationType.DEADLINE_ALERT,
            Notification.title.contains(
                deadline_key
            ),
            Notification.is_read.is_(False),
        )
    )

    if project_id is not None:
        query = query.filter(
            Notification.project_id == project_id
        )
    else:
        query = query.filter(
            Notification.project_id.is_(None)
        )

    return query.first() is not None


def _create_deadline_notification(
    db: Session,
    user: User,
    title: str,
    message: str,
    priority: NotificationPriority,
    deadline_key: str,
    project_id: int | None = None,
) -> bool:
    """
    Create a deadline notification only when the same
    deadline/state notification does not already exist.
    """

    if _notification_exists(
        db=db,
        user_id=user.id,
        deadline_key=deadline_key,
        project_id=project_id,
    ):
        return False

    notification = Notification(
        user_id=user.id,
        project_id=project_id,
        notification_type=NotificationType.DEADLINE_ALERT,
        priority=priority,
        title=title,
        message=message,
        is_read=False,
    )

    db.add(notification)

    return True


def _get_partner_users(
    db: Session,
    organization_id: int,
    allowed_roles: set[UserRole] | None = None,
) -> list[User]:
    """
    Get active partner users belonging to an organization.
    """

    if allowed_roles is None:
        allowed_roles = {
            UserRole.UNIVERSITY_ADMIN,
            UserRole.FACULTY,
            UserRole.INDUSTRY_ADMIN,
            UserRole.INDUSTRY_MEMBER,
        }

    return (
        db.query(User)
        .filter(
            User.organization_id == organization_id,
            User.is_active.is_(True),
            User.role.in_(list(allowed_roles)),
        )
        .all()
    )


def _get_unique_users(
    users: list[User],
) -> list[User]:
    """
    Remove duplicates while preserving users by ID.
    """

    return list(
        {
            user.id: user
            for user in users
        }.values()
    )


def _format_deadline_message(
    item_type: str,
    item_title: str,
    state_name: str,
) -> str:
    """
    Generate a consistent human-readable deadline message.
    """

    if state_name == "OVERDUE":
        return (
            f"{item_type} '{item_title}' "
            f"is overdue."
        )

    if state_name == "DUE_TODAY":
        return (
            f"{item_type} '{item_title}' "
            f"is due today."
        )

    days = int(
        state_name
        .replace("DUE_IN_", "")
        .replace("_DAYS", "")
    )

    return (
        f"{item_type} '{item_title}' "
        f"is due in {days} day(s)."
    )


# ============================================================
# RFP DEADLINES
# ============================================================

def _scan_rfp_deadlines(
    db: Session,
    now: datetime,
) -> int:

    rfps = (
        db.query(RFP)
        .filter(
            RFP.status == RFPStatus.PUBLISHED,
            RFP.proposal_deadline.isnot(None),
        )
        .all()
    )

    created = 0

    for rfp in rfps:

        deadline = _normalize_datetime(
            rfp.proposal_deadline
        )

        state = _get_deadline_state(
            deadline=deadline,
            now=now,
        )

        if state is None:
            continue

        state_name, priority = state

        invitations = (
            db.query(RFPInvitation)
            .filter(
                RFPInvitation.rfp_id == rfp.id,
            )
            .all()
        )

        for invitation in invitations:

            # ------------------------------------------------
            # No alert for invitations that no longer require
            # a university response.
            # ------------------------------------------------

            if invitation.status in {
                RFPInvitationStatus.DECLINED,
                RFPInvitationStatus.EXPIRED,
                RFPInvitationStatus.PROPOSAL_SUBMITTED,
            }:
                continue

            users = _get_partner_users(
                db=db,
                organization_id=invitation.university_id,
                allowed_roles={
                    UserRole.UNIVERSITY_ADMIN,
                    UserRole.FACULTY,
                },
            )

            deadline_key = (
                f"RFP:{rfp.id}:{state_name}"
            )

            title = (
                f"[{deadline_key}] "
                f"RFP deadline: {rfp.title}"
            )

            message = _format_deadline_message(
                item_type="RFP proposal deadline",
                item_title=rfp.title,
                state_name=state_name,
            )

            for user in users:

                if _create_deadline_notification(
                    db=db,
                    user=user,
                    title=title,
                    message=message,
                    priority=priority,
                    deadline_key=deadline_key,
                ):
                    created += 1

    return created


# ============================================================
# INDUSTRY COLLABORATION DEADLINES
# ============================================================

def _scan_collaboration_deadlines(
    db: Session,
    now: datetime,
) -> int:

    collaborations = (
        db.query(
            IndustryCollaborationProposal
        )
        .filter(
            IndustryCollaborationProposal.response_deadline.isnot(
                None
            ),
            IndustryCollaborationProposal.status.in_(
                [
                    IndustryCollaborationStatus.SUBMITTED,
                    IndustryCollaborationStatus.UNDER_REVIEW,
                    IndustryCollaborationStatus.MODIFICATION_REQUESTED,
                ]
            ),
        )
        .all()
    )

    created = 0

    for collaboration in collaborations:

        deadline = _normalize_datetime(
            collaboration.response_deadline
        )

        state = _get_deadline_state(
            deadline=deadline,
            now=now,
        )

        if state is None:
            continue

        state_name, priority = state

        # Ensure linked university proposal exists.
        university_proposal = (
            collaboration.university_proposal
        )

        if not university_proposal:
            continue

        users = _get_partner_users(
            db=db,
            organization_id=collaboration.industry_id,
            allowed_roles={
                UserRole.INDUSTRY_ADMIN,
                UserRole.INDUSTRY_MEMBER,
            },
        )

        deadline_key = (
            f"COLLABORATION:{collaboration.id}:"
            f"{state_name}"
        )

        title = (
            f"[{deadline_key}] "
            "Industry collaboration response deadline"
        )

        message = _format_deadline_message(
            item_type="Industry collaboration response",
            item_title=(
                f"proposal #{collaboration.id}"
            ),
            state_name=state_name,
        )

        for user in users:

            if _create_deadline_notification(
                db=db,
                user=user,
                title=title,
                message=message,
                priority=priority,
                deadline_key=deadline_key,
            ):
                created += 1

    return created


# ============================================================
# MILESTONE DEADLINES
# ============================================================

def _scan_milestone_deadlines(
    db: Session,
    now: datetime,
) -> int:

    milestones = (
        db.query(ProjectMilestone)
        .join(
            Project,
            ProjectMilestone.project_id
            == Project.id,
        )
        .filter(
            ProjectMilestone.due_date.isnot(None),
            ProjectMilestone.status.notin_(
                [
                    ProjectMilestoneStatus.COMPLETED,
                ]
            ),
        )
        .all()
    )

    created = 0

    for milestone in milestones:

        deadline = _normalize_datetime(
            milestone.due_date
        )

        state = _get_deadline_state(
            deadline=deadline,
            now=now,
        )

        if state is None:
            continue

        state_name, priority = state

        project = milestone.project

        if not project:
            continue

        users: list[User] = []

        # ----------------------------------------------------
        # University users
        # ----------------------------------------------------

        if project.university_id:
            users.extend(
                _get_partner_users(
                    db=db,
                    organization_id=(
                        project.university_id
                    ),
                    allowed_roles={
                        UserRole.UNIVERSITY_ADMIN,
                        UserRole.FACULTY,
                    },
                )
            )

        # ----------------------------------------------------
        # Industry users
        # ----------------------------------------------------

        if project.industry_id:
            users.extend(
                _get_partner_users(
                    db=db,
                    organization_id=(
                        project.industry_id
                    ),
                    allowed_roles={
                        UserRole.INDUSTRY_ADMIN,
                        UserRole.INDUSTRY_MEMBER,
                    },
                )
            )

        unique_users = _get_unique_users(
            users
        )

        deadline_key = (
            f"MILESTONE:{milestone.id}:{state_name}"
        )

        title = (
            f"[{deadline_key}] "
            f"Milestone deadline: {milestone.title}"
        )

        message = _format_deadline_message(
            item_type="Milestone",
            item_title=(
                f"{milestone.title} "
                f"(project: {project.title})"
            ),
            state_name=state_name,
        )

        for user in unique_users:

            if _create_deadline_notification(
                db=db,
                user=user,
                title=title,
                message=message,
                priority=priority,
                deadline_key=deadline_key,
                project_id=project.id,
            ):
                created += 1

    return created


# ============================================================
# DELIVERABLE DEADLINES
# ============================================================

def _scan_deliverable_deadlines(
    db: Session,
    now: datetime,
) -> int:

    deliverables = (
        db.query(ProjectDeliverable)
        .join(
            Project,
            ProjectDeliverable.project_id
            == Project.id,
        )
        .filter(
            ProjectDeliverable.due_date.isnot(None),
            ProjectDeliverable.status.notin_(
                [
                    ProjectDeliverableStatus.APPROVED,
                ]
            ),
        )
        .all()
    )

    created = 0

    for deliverable in deliverables:

        deadline = _normalize_datetime(
            deliverable.due_date
        )

        state = _get_deadline_state(
            deadline=deadline,
            now=now,
        )

        if state is None:
            continue

        state_name, priority = state

        project = deliverable.project

        if not project:
            continue

        users: list[User] = []

        # ----------------------------------------------------
        # University users
        # ----------------------------------------------------

        if project.university_id:
            users.extend(
                _get_partner_users(
                    db=db,
                    organization_id=(
                        project.university_id
                    ),
                    allowed_roles={
                        UserRole.UNIVERSITY_ADMIN,
                        UserRole.FACULTY,
                    },
                )
            )

        # ----------------------------------------------------
        # Industry users
        # ----------------------------------------------------

        if project.industry_id:
            users.extend(
                _get_partner_users(
                    db=db,
                    organization_id=(
                        project.industry_id
                    ),
                    allowed_roles={
                        UserRole.INDUSTRY_ADMIN,
                        UserRole.INDUSTRY_MEMBER,
                    },
                )
            )

        unique_users = _get_unique_users(
            users
        )

        deadline_key = (
            f"DELIVERABLE:{deliverable.id}:"
            f"{state_name}"
        )

        title = (
            f"[{deadline_key}] "
            f"Deliverable deadline: "
            f"{deliverable.title}"
        )

        message = _format_deadline_message(
            item_type="Deliverable",
            item_title=(
                f"{deliverable.title} "
                f"(project: {project.title})"
            ),
            state_name=state_name,
        )

        for user in unique_users:

            if _create_deadline_notification(
                db=db,
                user=user,
                title=title,
                message=message,
                priority=priority,
                deadline_key=deadline_key,
                project_id=project.id,
            ):
                created += 1

    return created


# ============================================================
# MASTER DEADLINE SCAN
# ============================================================

def run_deadline_scan(
    db: Session,
) -> dict:

    now = datetime.now(timezone.utc)

    created = {
        "rfp": 0,
        "collaboration": 0,
        "milestones": 0,
        "deliverables": 0,
        "total": 0,
    }

    try:
        created["rfp"] = _scan_rfp_deadlines(
            db=db,
            now=now,
        )

        created["collaboration"] = (
            _scan_collaboration_deadlines(
                db=db,
                now=now,
            )
        )

        created["milestones"] = (
            _scan_milestone_deadlines(
                db=db,
                now=now,
            )
        )

        created["deliverables"] = (
            _scan_deliverable_deadlines(
                db=db,
                now=now,
            )
        )

        created["total"] = sum(
            value
            for key, value in created.items()
            if key != "total"
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    return created