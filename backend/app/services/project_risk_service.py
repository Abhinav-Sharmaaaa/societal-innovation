from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_deliverable import (
    ProjectDeliverable,
    ProjectDeliverableStatus,
)
from app.models.project_funding import (
    FundingTransactionStatus,
    FundingTransactionType,
    ProjectFundingTransaction,
)
from app.models.project_milestone import (
    ProjectMilestone,
    ProjectMilestoneStatus,
)
from app.models.project_outcome import (
    ProjectOutcome,
    ProjectOutcomeStatus,
)
from app.models.project_report import (
    ProjectReport,
    ProjectReportStatus,
)
from app.models.project_risk import (
    ProjectRisk,
    ProjectRiskLevel,
    ProjectRiskStatus,
)
from app.models.user import User, UserRole
from app.services.notification_service import (
    notify_government_of_risk,
)


GOVERNMENT_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.GOVERNMENT_OFFICER,
    UserRole.MUNICIPALITY_OFFICER,
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


def _calculate_funding_metrics(
    db: Session,
    project_id: int,
) -> tuple[float, float, float]:
    transactions = (
        db.query(ProjectFundingTransaction)
        .filter(
            ProjectFundingTransaction.project_id == project_id,
            ProjectFundingTransaction.status
            == FundingTransactionStatus.COMPLETED,
        )
        .all()
    )

    allocated = 0.0
    disbursed = 0.0
    utilized = 0.0

    for transaction in transactions:
        if transaction.transaction_type == (
            FundingTransactionType.ALLOCATION
        ):
            allocated += transaction.amount

        elif transaction.transaction_type == (
            FundingTransactionType.DISBURSEMENT
        ):
            disbursed += transaction.amount

        elif transaction.transaction_type == (
            FundingTransactionType.UTILIZATION
        ):
            utilized += transaction.amount

    return allocated, disbursed, utilized


def calculate_project_risk(
    db: Session,
    project_id: int,
) -> dict:
    project = _get_project(
        db,
        project_id,
    )

    now = datetime.now(timezone.utc)

    milestones = (
        db.query(ProjectMilestone)
        .filter(
            ProjectMilestone.project_id == project.id
        )
        .all()
    )

    deliverables = (
        db.query(ProjectDeliverable)
        .filter(
            ProjectDeliverable.project_id == project.id
        )
        .all()
    )

    reports = (
        db.query(ProjectReport)
        .filter(
            ProjectReport.project_id == project.id
        )
        .all()
    )

    outcomes = (
        db.query(ProjectOutcome)
        .filter(
            ProjectOutcome.project_id == project.id
        )
        .all()
    )

    score = 0.0
    factors: list[str] = []

    # ---------------------------------------------------------
    # 1. Delayed milestones
    # ---------------------------------------------------------
    delayed_milestones = [
        milestone
        for milestone in milestones
        if milestone.status
        == ProjectMilestoneStatus.DELAYED
    ]

    delayed_count = len(delayed_milestones)

    if delayed_count:
        score += min(
            delayed_count * 15,
            30,
        )

        factors.append(
            f"{delayed_count} milestone(s) are delayed."
        )

    # ---------------------------------------------------------
    # 2. Blocked milestones
    # ---------------------------------------------------------
    blocked_milestones = [
        milestone
        for milestone in milestones
        if milestone.status
        == ProjectMilestoneStatus.BLOCKED
    ]

    blocked_count = len(blocked_milestones)

    if blocked_count:
        score += min(
            blocked_count * 25,
            50,
        )

        factors.append(
            f"{blocked_count} milestone(s) are blocked."
        )

    # ---------------------------------------------------------
    # 3. Overdue milestones
    # ---------------------------------------------------------
    overdue_milestones = [
        milestone
        for milestone in milestones
        if (
            milestone.due_date is not None
            and milestone.due_date < now
            and milestone.status
            != ProjectMilestoneStatus.COMPLETED
        )
    ]

    overdue_milestone_count = len(
        overdue_milestones
    )

    if overdue_milestone_count:
        score += min(
            overdue_milestone_count * 10,
            25,
        )

        factors.append(
            f"{overdue_milestone_count} milestone(s) "
            "are past their due date."
        )

    # ---------------------------------------------------------
    # 4. Overdue deliverables
    # ---------------------------------------------------------
    overdue_deliverables = [
        deliverable
        for deliverable in deliverables
        if (
            deliverable.due_date is not None
            and deliverable.due_date < now
            and deliverable.status
            != ProjectDeliverableStatus.APPROVED
        )
    ]

    overdue_deliverable_count = len(
        overdue_deliverables
    )

    if overdue_deliverable_count:
        score += min(
            overdue_deliverable_count * 8,
            24,
        )

        factors.append(
            f"{overdue_deliverable_count} deliverable(s) "
            "are overdue."
        )

    # ---------------------------------------------------------
    # 5. Rejected reports
    # ---------------------------------------------------------
    rejected_reports = [
        report
        for report in reports
        if report.status
        == ProjectReportStatus.REJECTED
    ]

    rejected_report_count = len(
        rejected_reports
    )

    if rejected_report_count:
        score += min(
            rejected_report_count * 5,
            15,
        )

        factors.append(
            f"{rejected_report_count} project report(s) "
            "have been rejected."
        )

    # ---------------------------------------------------------
    # 6. Schedule deviation
    # ---------------------------------------------------------
    if (
        project.start_date is not None
        and project.target_completion_date is not None
    ):
        total_duration = (
            project.target_completion_date
            - project.start_date
        ).total_seconds()

        elapsed_duration = (
            now - project.start_date
        ).total_seconds()

        if total_duration > 0:
            expected_progress = min(
                max(
                    elapsed_duration
                    / total_duration
                    * 100,
                    0,
                ),
                100,
            )

            actual_progress = (
                project.progress_percentage or 0
            )

            progress_gap = (
                expected_progress
                - actual_progress
            )

            if progress_gap >= 30:
                score += 25

                factors.append(
                    f"Project progress is approximately "
                    f"{progress_gap:.1f}% behind the expected schedule."
                )

            elif progress_gap >= 15:
                score += 15

                factors.append(
                    f"Project progress is approximately "
                    f"{progress_gap:.1f}% behind the expected schedule."
                )

            elif progress_gap >= 8:
                score += 8

                factors.append(
                    f"Project progress is approximately "
                    f"{progress_gap:.1f}% behind the expected schedule."
                )

    # ---------------------------------------------------------
    # 7. Funding utilization vs project progress
    # ---------------------------------------------------------
    allocated, _, utilized = _calculate_funding_metrics(
        db,
        project.id,
    )

    if allocated > 0:
        utilization_percentage = (
            utilized / allocated
        ) * 100

        progress = (
            project.progress_percentage or 0
        )

        if (
            utilization_percentage >= 80
            and progress < 50
        ):
            score += 20

            factors.append(
                f"{utilization_percentage:.1f}% of allocated "
                "funding has been utilized while project "
                f"progress is only {progress:.1f}%."
            )

        elif (
            utilization_percentage >= 60
            and progress < 40
        ):
            score += 12

            factors.append(
                f"Funding utilization is "
                f"{utilization_percentage:.1f}% against "
                f"{progress:.1f}% project progress."
            )

    # ---------------------------------------------------------
    # 8. Outcome underperformance
    # ---------------------------------------------------------
    verified_outcomes = [
        outcome
        for outcome in outcomes
        if outcome.status
        == ProjectOutcomeStatus.VERIFIED
    ]

    underperforming_outcomes = 0

    for outcome in verified_outcomes:
        if (
            outcome.target_value is not None
            and outcome.achieved_value is not None
            and outcome.target_value > 0
            and outcome.achieved_value < outcome.target_value
        ):
            underperforming_outcomes += 1

    if underperforming_outcomes:
        score += min(
            underperforming_outcomes * 10,
            20,
        )

        factors.append(
            f"{underperforming_outcomes} verified "
            "outcome metric(s) are below target."
        )

    # ---------------------------------------------------------
    # Final score
    # ---------------------------------------------------------
    score = round(
        min(score, 100),
        2,
    )

    # ---------------------------------------------------------
    # Risk level
    # ---------------------------------------------------------
    if score >= 75:
        risk_level = ProjectRiskLevel.CRITICAL
    elif score >= 50:
        risk_level = ProjectRiskLevel.HIGH
    elif score >= 25:
        risk_level = ProjectRiskLevel.MEDIUM
    else:
        risk_level = ProjectRiskLevel.LOW

    # ---------------------------------------------------------
    # Recommended action
    # ---------------------------------------------------------
    if risk_level == ProjectRiskLevel.CRITICAL:
        recommended_action = (
            "Immediate government intervention is recommended. "
            "Review blocked milestones, schedule recovery, "
            "funding utilization, and corrective actions."
        )

    elif risk_level == ProjectRiskLevel.HIGH:
        recommended_action = (
            "Initiate a corrective-action review with the "
            "university and industry partners."
        )

    elif risk_level == ProjectRiskLevel.MEDIUM:
        recommended_action = (
            "Increase monitoring frequency and review the "
            "affected milestones and deliverables."
        )

    else:
        recommended_action = (
            "Continue routine monitoring. No immediate "
            "intervention is indicated."
        )

    if not factors:
        factors.append(
            "No significant execution risk factors detected."
        )

    return {
        "project_id": project.id,
        "risk_score": score,
        "risk_level": risk_level.value,
        "detected_factors": factors,
        "recommended_action": recommended_action,
    }


def run_project_risk_assessment(
    db: Session,
    project_id: int,
    current_user: User,
) -> ProjectRisk:

    if current_user.role not in GOVERNMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users can "
                "run project risk assessments."
            ),
        )

    project = _get_project(
        db,
        project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    assessment = calculate_project_risk(
        db,
        project_id,
    )

    previous_risk = (
        db.query(ProjectRisk)
        .filter(
            ProjectRisk.project_id == project.id,
            ProjectRisk.status.in_(
                {
                    ProjectRiskStatus.OPEN,
                    ProjectRiskStatus.ACKNOWLEDGED,
                    ProjectRiskStatus.MITIGATED,
                }
            ),
        )
        .order_by(
            ProjectRisk.detected_at.desc()
        )
        .first()
    )

    previous_level = (
        previous_risk.risk_level
        if previous_risk
        else None
    )

    previous_score = (
        previous_risk.risk_score
        if previous_risk
        else None
    )

    detected_factors = "\n".join(
        f"- {factor}"
        for factor in assessment["detected_factors"]
    )

    if previous_risk:
        risk = previous_risk

        risk.risk_level = ProjectRiskLevel(
            assessment["risk_level"]
        )

        risk.risk_score = assessment["risk_score"]

        risk.title = (
            f"Project risk assessment "
            f"({assessment['risk_level']})"
        )

        risk.description = (
            "Automated execution-risk assessment "
            "based on current project signals."
        )

        risk.detected_factors = detected_factors

        risk.recommended_action = (
            assessment["recommended_action"]
        )

    else:
        risk = ProjectRisk(
            project_id=project.id,
            risk_level=ProjectRiskLevel(
                assessment["risk_level"]
            ),
            risk_score=assessment["risk_score"],
            title=(
                f"Project risk assessment "
                f"({assessment['risk_level']})"
            ),
            description=(
                "Automated execution-risk assessment "
                "based on current project signals."
            ),
            detected_factors=detected_factors,
            recommended_action=(
                assessment["recommended_action"]
            ),
            status=ProjectRiskStatus.OPEN,
        )

        db.add(risk)

    db.commit()
    db.refresh(risk)

    # ---------------------------------------------------------
    # Notify only for meaningful risk escalation
    # ---------------------------------------------------------
    should_notify = (
        previous_risk is None
        or previous_level != risk.risk_level
        or (
            previous_score is not None
            and risk.risk_score >= previous_score + 10
        )
    )

    if (
        should_notify
        and risk.risk_level
        in {
            ProjectRiskLevel.HIGH,
            ProjectRiskLevel.CRITICAL,
        }
    ):
        notify_government_of_risk(
            db=db,
            project=project,
            risk=risk,
        )

    return risk


def update_project_risk_status(
    db: Session,
    risk_id: int,
    action: str,
    remarks: str | None,
    current_user: User,
) -> ProjectRisk:

    if current_user.role not in GOVERNMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users can "
                "manage project risks."
            ),
        )

    risk = (
        db.query(ProjectRisk)
        .filter(
            ProjectRisk.id == risk_id
        )
        .first()
    )

    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project risk not found.",
        )

    project = risk.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    now = datetime.now(timezone.utc)

    allowed_transitions = {
        ProjectRiskStatus.OPEN: {
            ProjectRiskStatus.ACKNOWLEDGED,
        },
        ProjectRiskStatus.ACKNOWLEDGED: {
            ProjectRiskStatus.MITIGATED,
        },
        ProjectRiskStatus.MITIGATED: {
            ProjectRiskStatus.CLOSED,
        },
    }

    current_status = risk.status

    try:
        target_status = ProjectRiskStatus(action)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid risk action.",
        ) from exc

    if target_status not in allowed_transitions.get(
        current_status,
        set(),
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Risk cannot transition from "
                f"{current_status.value} to "
                f"{target_status.value}."
            ),
        )

    risk.status = target_status

    if target_status == ProjectRiskStatus.ACKNOWLEDGED:
        risk.acknowledged_at = now

    elif target_status == ProjectRiskStatus.MITIGATED:
        risk.resolution_remarks = remarks

    elif target_status == ProjectRiskStatus.CLOSED:
        risk.resolved_at = now

        if remarks:
            risk.resolution_remarks = remarks

    db.commit()
    db.refresh(risk)

    return risk