from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_evidence import (
    ProjectEvidence,
    ProjectEvidenceType,
)
from app.models.project_milestone import ProjectMilestone
from app.models.project_report import (
    ProjectReport,
    ProjectReportStatus,
    ProjectReportType,
)
from app.models.user import User, UserRole
from app.schemas.project_evidence import (
    ProjectEvidenceCreate,
)
from app.schemas.project_report import (
    ProjectReportCreate,
    ProjectReportReview,
)


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
        .filter(Project.id == project_id)
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
                detail="Government user is not associated with an organization.",
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


def create_project_report(
    db: Session,
    report_data: ProjectReportCreate,
    current_user: User,
) -> ProjectReport:

    project = _get_project(
        db,
        report_data.project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    if current_user.role not in PARTNER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only university or industry project partners can submit reports.",
        )

    milestone = None

    if report_data.milestone_id is not None:
        milestone = (
            db.query(ProjectMilestone)
            .filter(
                ProjectMilestone.id
                == report_data.milestone_id
            )
            .first()
        )

        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found.",
            )

        if milestone.project_id != project.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Milestone does not belong to this project.",
            )

    report = ProjectReport(
        project_id=project.id,
        milestone_id=(
            milestone.id
            if milestone
            else None
        ),
        submitted_by=current_user.id,
        report_type=ProjectReportType(
            report_data.report_type
        ),
        title=report_data.title,
        summary=report_data.summary,
        findings=report_data.findings,
        challenges=report_data.challenges,
        next_steps=report_data.next_steps,
        status=ProjectReportStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc),
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def review_project_report(
    db: Session,
    report_id: int,
    review_data: ProjectReportReview,
    current_user: User,
) -> ProjectReport:

    if current_user.role not in GOVERNMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized government users can review reports.",
        )

    report = (
        db.query(ProjectReport)
        .filter(
            ProjectReport.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project report not found.",
        )

    project = report.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if report.status not in {
        ProjectReportStatus.SUBMITTED,
        ProjectReportStatus.UNDER_REVIEW,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This report cannot be reviewed in its current state.",
        )

    report.status = ProjectReportStatus(
        review_data.decision
    )

    report.reviewed_at = datetime.now(timezone.utc)
    report.review_remarks = (
        review_data.review_remarks
    )

    db.commit()
    db.refresh(report)

    return report


def create_project_evidence(
    db: Session,
    evidence_data: ProjectEvidenceCreate,
    current_user: User,
) -> ProjectEvidence:

    project = _get_project(
        db,
        evidence_data.project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    if current_user.role not in PARTNER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only university or industry project partners can upload evidence.",
        )

    if not evidence_data.file_url and not evidence_data.external_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either file_url or external_url is required.",
        )

    if evidence_data.report_id is not None:
        report = (
            db.query(ProjectReport)
            .filter(
                ProjectReport.id
                == evidence_data.report_id
            )
            .first()
        )

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        if report.project_id != project.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report does not belong to this project.",
            )

    evidence = ProjectEvidence(
        project_id=project.id,
        report_id=evidence_data.report_id,
        uploaded_by=current_user.id,
        evidence_type=ProjectEvidenceType(
            evidence_data.evidence_type
        ),
        title=evidence_data.title,
        file_url=evidence_data.file_url,
        external_url=evidence_data.external_url,
        description=evidence_data.description,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def list_project_reports(
    db: Session,
    project_id: int,
    current_user: User,
) -> list[ProjectReport]:

    project = _get_project(
        db,
        project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    return (
        db.query(ProjectReport)
        .filter(
            ProjectReport.project_id == project_id
        )
        .order_by(
            ProjectReport.created_at.desc()
        )
        .all()
    )


def list_project_evidence(
    db: Session,
    project_id: int,
    current_user: User,
) -> list[ProjectEvidence]:

    project = _get_project(
        db,
        project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    return (
        db.query(ProjectEvidence)
        .filter(
            ProjectEvidence.project_id == project_id
        )
        .order_by(
            ProjectEvidence.created_at.desc()
        )
        .all()
    )