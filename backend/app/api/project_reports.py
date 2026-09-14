from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.project_evidence import (
    ProjectEvidenceCreate,
    ProjectEvidenceResponse,
)
from app.schemas.project_report import (
    ProjectReportCreate,
    ProjectReportResponse,
    ProjectReportReview,
)
from app.services.project_report_service import (
    create_project_evidence,
    create_project_report,
    list_project_evidence,
    list_project_reports,
    review_project_report,
)


router = APIRouter(
    prefix="/project-reports",
    tags=["Project Reports"],
)


@router.post(
    "",
    response_model=ProjectReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    report_data: ProjectReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project_report(
        db=db,
        report_data=report_data,
        current_user=current_user,
    )


@router.post(
    "/{report_id}/review",
    response_model=ProjectReportResponse,
)
def review_report(
    report_id: int,
    review_data: ProjectReportReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return review_project_report(
        db=db,
        report_id=report_id,
        review_data=review_data,
        current_user=current_user,
    )


@router.get(
    "/project/{project_id}",
    response_model=list[ProjectReportResponse],
)
def get_project_reports(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_project_reports(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )


@router.post(
    "/evidence",
    response_model=ProjectEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence(
    evidence_data: ProjectEvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project_evidence(
        db=db,
        evidence_data=evidence_data,
        current_user=current_user,
    )


@router.get(
    "/project/{project_id}/evidence",
    response_model=list[ProjectEvidenceResponse],
)
def get_project_evidence(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_project_evidence(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )