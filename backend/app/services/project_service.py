from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.industry_collaboration import (
    IndustryCollaborationProposal,
    IndustryCollaborationStatus,
)
from app.models.project import (
    Project,
    ProjectHealth,
    ProjectStatus,
)
from app.models.project_milestone import (
    ProjectMilestone,
    ProjectMilestoneStatus,
    ProjectMilestoneType,
)
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate


MILESTONE_DEFINITIONS = [
    {
        "type": ProjectMilestoneType.PROBLEM_VALIDATION,
        "sequence": 1,
        "title": "Problem Validation",
        "description": (
            "Validate the societal problem, stakeholders, "
            "requirements, and field conditions."
        ),
        "deliverables": (
            "Validated problem statement, stakeholder findings, "
            "and requirement baseline."
        ),
    },
    {
        "type": ProjectMilestoneType.RESEARCH_PLANNING,
        "sequence": 2,
        "title": "Research & Planning",
        "description": (
            "Finalize research methodology, technical architecture, "
            "resources, and implementation roadmap."
        ),
        "deliverables": (
            "Research plan, technical architecture, resource plan, "
            "and implementation schedule."
        ),
    },
    {
        "type": ProjectMilestoneType.PROTOTYPE_DEVELOPMENT,
        "sequence": 3,
        "title": "Prototype Development",
        "description": (
            "Develop the initial working prototype of the solution."
        ),
        "deliverables": (
            "Working prototype, source implementation, "
            "and technical documentation."
        ),
    },
    {
        "type": ProjectMilestoneType.TESTING_VALIDATION,
        "sequence": 4,
        "title": "Testing & Validation",
        "description": (
            "Test and validate the prototype against technical, "
            "functional, and societal requirements."
        ),
        "deliverables": (
            "Test results, validation report, identified issues, "
            "and corrective actions."
        ),
    },
    {
        "type": ProjectMilestoneType.PILOT_DEPLOYMENT,
        "sequence": 5,
        "title": "Pilot Deployment",
        "description": (
            "Deploy the validated solution in the selected pilot environment."
        ),
        "deliverables": (
            "Pilot deployment, field feedback, usage metrics, "
            "and pilot performance report."
        ),
    },
    {
        "type": ProjectMilestoneType.FINAL_SOLUTION_DEPLOYMENT,
        "sequence": 6,
        "title": "Final Solution / Deployment",
        "description": (
            "Finalize, deploy, and hand over the production-ready solution."
        ),
        "deliverables": (
            "Final solution, deployment documentation, outcome report, "
            "and handover package."
        ),
    },
]


def _check_project_access(
    project: Project,
    current_user: User,
) -> None:
    """
    Verify that the current user is allowed to access the project.
    """

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


def create_project(
    db: Session,
    project_data: ProjectCreate,
    current_user: User,
) -> Project:

    # ---------------------------------------------------------
    # 1. Authorization
    # ---------------------------------------------------------
    if current_user.role not in {
        UserRole.SUPER_ADMIN,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.MUNICIPALITY_OFFICER,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users "
                "can create projects."
            ),
        )

    # ---------------------------------------------------------
    # 2. Load collaboration
    # ---------------------------------------------------------
    collaboration = (
        db.query(IndustryCollaborationProposal)
        .filter(
            IndustryCollaborationProposal.id
            == project_data.collaboration_id
        )
        .first()
    )

    if not collaboration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Industry collaboration proposal not found.",
        )

    # ---------------------------------------------------------
    # 3. Collaboration must be accepted
    # ---------------------------------------------------------
    if collaboration.status != IndustryCollaborationStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A project can only be created from an "
                "accepted industry collaboration proposal."
            ),
        )

    # ---------------------------------------------------------
    # 4. Prevent duplicate project
    # ---------------------------------------------------------
    existing_project = (
        db.query(Project)
        .filter(
            Project.collaboration_id == collaboration.id
        )
        .first()
    )

    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "A project already exists for this collaboration."
            ),
        )

    # ---------------------------------------------------------
    # 5. Load university proposal
    # ---------------------------------------------------------
    university_proposal = collaboration.university_proposal

    if not university_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated university proposal not found.",
        )

    # ---------------------------------------------------------
    # 6. Resolve challenge safely
    # ---------------------------------------------------------
    rfp = university_proposal.rfp

    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated RFP not found.",
        )

    opportunity = rfp.innovation_opportunity

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated innovation opportunity not found.",
        )

    challenge = opportunity.challenge

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated challenge not found.",
        )

    # ---------------------------------------------------------
    # 7. Determine project dates
    # ---------------------------------------------------------
    now = datetime.now(timezone.utc)

    start_date = project_data.start_date or now

    if project_data.target_completion_date:
        target_completion_date = (
            project_data.target_completion_date
        )
    else:
        duration_days = (
            collaboration.proposed_duration_days
            or university_proposal.expected_timeline_days
            or 180
        )

        target_completion_date = (
            start_date + timedelta(days=duration_days)
        )

    # Normalize naive datetimes
    if start_date.tzinfo is None:
        start_date = start_date.replace(
            tzinfo=timezone.utc
        )

    if target_completion_date.tzinfo is None:
        target_completion_date = (
            target_completion_date.replace(
                tzinfo=timezone.utc
            )
        )

    if target_completion_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Target completion date must be "
                "after the start date."
            ),
        )

    # ---------------------------------------------------------
    # 8. Create project
    # ---------------------------------------------------------
    project = Project(
        collaboration_id=collaboration.id,
        challenge_id=challenge.id,
        university_id=university_proposal.university_id,
        industry_id=collaboration.industry_id,
        created_by=current_user.id,
        title=project_data.title,
        description=project_data.description,
        objectives=project_data.objectives,
        expected_outcomes=project_data.expected_outcomes,
        total_budget=(
            project_data.total_budget
            if project_data.total_budget is not None
            else collaboration.funding_amount
        ),
        start_date=start_date,
        target_completion_date=target_completion_date,
        status=ProjectStatus.PLANNING,
        health=ProjectHealth.ON_TRACK,
        progress_percentage=0,
    )

    db.add(project)
    db.flush()

    # ---------------------------------------------------------
    # 9. Automatically create six milestones
    # ---------------------------------------------------------
    total_duration_seconds = (
        target_completion_date - start_date
    ).total_seconds()

    milestone_count = len(MILESTONE_DEFINITIONS)

    for index, definition in enumerate(
        MILESTONE_DEFINITIONS
    ):
        milestone_start = (
            start_date
            + timedelta(
                seconds=(
                    total_duration_seconds
                    * index
                    / milestone_count
                )
            )
        )

        milestone_due = (
            start_date
            + timedelta(
                seconds=(
                    total_duration_seconds
                    * (index + 1)
                    / milestone_count
                )
            )
        )

        milestone = ProjectMilestone(
            project_id=project.id,
            milestone_type=definition["type"],
            sequence_number=definition["sequence"],
            title=definition["title"],
            description=definition["description"],
            deliverables=definition["deliverables"],
            start_date=milestone_start,
            due_date=milestone_due,
            status=ProjectMilestoneStatus.NOT_STARTED,
            progress_percentage=0,
            is_mandatory=True,
        )

        db.add(milestone)

    # ---------------------------------------------------------
    # 10. Commit
    # ---------------------------------------------------------
    db.commit()
    db.refresh(project)

    return project


def get_project(
    db: Session,
    project_id: int,
    current_user: User,
) -> Project:

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    return project


def list_projects(
    db: Session,
    current_user: User,
) -> list[Project]:

    query = db.query(Project)

    # ---------------------------------------------------------
    # SUPER_ADMIN
    # ---------------------------------------------------------
    if current_user.role == UserRole.SUPER_ADMIN:
        return (
            query
            .order_by(Project.created_at.desc())
            .all()
        )

    # ---------------------------------------------------------
    # GOVERNMENT
    #
    # Government users can currently view all projects.
    # Organization-level jurisdiction can be tightened later
    # when project jurisdiction rules are finalized.
    # ---------------------------------------------------------
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

        return (
            query
            .order_by(Project.created_at.desc())
            .all()
        )

    # ---------------------------------------------------------
    # UNIVERSITY
    # ---------------------------------------------------------
    if current_user.role in {
        UserRole.UNIVERSITY_ADMIN,
        UserRole.FACULTY,
    }:
        if current_user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "University user is not associated "
                    "with an organization."
                ),
            )

        return (
            query
            .filter(
                Project.university_id
                == current_user.organization_id
            )
            .order_by(Project.created_at.desc())
            .all()
        )

    # ---------------------------------------------------------
    # INDUSTRY
    # ---------------------------------------------------------
    if current_user.role in {
        UserRole.INDUSTRY_ADMIN,
        UserRole.INDUSTRY_MEMBER,
    }:
        if current_user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Industry user is not associated "
                    "with an organization."
                ),
            )

        return (
            query
            .filter(
                Project.industry_id
                == current_user.organization_id
            )
            .order_by(Project.created_at.desc())
            .all()
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to access projects.",
    )