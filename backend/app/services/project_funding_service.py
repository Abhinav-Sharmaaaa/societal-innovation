from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_funding import (
    FundingTransactionStatus,
    FundingTransactionType,
    ProjectFundingTransaction,
)
from app.models.reputation import ReputationEventType
from app.models.user import User, UserRole
from app.schemas.project_funding import (
    ProjectFundingApproval,
    ProjectFundingCreate,
)
from app.services.reputation_service import award_reputation_points


GOVERNMENT_ROLES = {
    UserRole.SUPER_ADMIN,
    UserRole.GOVERNMENT_OFFICER,
    UserRole.MUNICIPALITY_OFFICER,
}


PROJECT_PARTNER_ROLES = {
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


def create_funding_transaction(
    db: Session,
    funding_data: ProjectFundingCreate,
    current_user: User,
) -> ProjectFundingTransaction:

    project = _get_project(
        db,
        funding_data.project_id,
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
                "Funding transactions cannot be added "
                "to a completed or cancelled project."
            ),
        )

    transaction_type = FundingTransactionType(
        funding_data.transaction_type
    )

    transaction = ProjectFundingTransaction(
        project_id=project.id,
        transaction_type=transaction_type,
        status=FundingTransactionStatus.PENDING,
        amount=funding_data.amount,
        transaction_date=(
            funding_data.transaction_date
            or datetime.now(timezone.utc)
        ),
        description=funding_data.description,
        reference_number=funding_data.reference_number,
        created_by=current_user.id,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def approve_funding_transaction(
    db: Session,
    transaction_id: int,
    approval_data: ProjectFundingApproval,
    current_user: User,
) -> ProjectFundingTransaction:

    if current_user.role not in GOVERNMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users can "
                "approve funding transactions."
            ),
        )

    transaction = (
        db.query(ProjectFundingTransaction)
        .filter(
            ProjectFundingTransaction.id
            == transaction_id
        )
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding transaction not found.",
        )

    project = transaction.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if transaction.status != FundingTransactionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only pending funding transactions "
                "can be reviewed."
            ),
        )

    now = datetime.now(timezone.utc)

    if approval_data.decision == "APPROVED":
        transaction.status = FundingTransactionStatus.APPROVED
        transaction.approved_by = current_user.id
        transaction.approved_at = now

    else:
        transaction.status = FundingTransactionStatus.REJECTED
        transaction.approved_by = current_user.id
        transaction.approved_at = now

    if approval_data.remarks:
        transaction.description = (
            f"{transaction.description or ''}"
            f"\n\nApproval remarks: "
            f"{approval_data.remarks}"
        ).strip()

    db.commit()
    db.refresh(transaction)

    return transaction


def complete_funding_transaction(
    db: Session,
    transaction_id: int,
    current_user: User,
) -> ProjectFundingTransaction:

    if current_user.role not in GOVERNMENT_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized government users can "
                "complete funding transactions."
            ),
        )

    transaction = (
        db.query(ProjectFundingTransaction)
        .filter(
            ProjectFundingTransaction.id
            == transaction_id
        )
        .first()
    )

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding transaction not found.",
        )

    project = transaction.project

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated project not found.",
        )

    _check_project_access(
        project,
        current_user,
    )

    if transaction.status != FundingTransactionStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only approved funding transactions "
                "can be completed."
            ),
        )

    # ---------------------------------------------------------
    # Complete transaction
    # ---------------------------------------------------------
    transaction.status = FundingTransactionStatus.COMPLETED

    db.commit()
    db.refresh(transaction)

    # ---------------------------------------------------------
    # Industry reputation
    #
    # A completed project funding transaction awards +25
    # reputation to the project's industry partner.
    #
    # The transaction ID is embedded in the description so
    # reputation_service.py can prevent duplicate awards.
    # ---------------------------------------------------------
    if project.industry_id is not None:

        award_reputation_points(
            db=db,
            event_type=(
                ReputationEventType.FUNDING_CONTRIBUTION
            ),
            description=(
                f"Funding contribution completed: "
                f"transaction_id={transaction.id}"
            ),
            organization_id=project.industry_id,
            project_id=project.id,
        )

        db.refresh(transaction)

    return transaction


def get_project_funding_summary(
    db: Session,
    project_id: int,
    current_user: User,
) -> dict:

    project = _get_project(
        db,
        project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    transactions = (
        db.query(ProjectFundingTransaction)
        .filter(
            ProjectFundingTransaction.project_id
            == project_id,
            ProjectFundingTransaction.status
            == FundingTransactionStatus.COMPLETED,
        )
        .all()
    )

    allocated = 0.0
    disbursed = 0.0
    utilized = 0.0
    refunded = 0.0

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

        elif transaction.transaction_type == (
            FundingTransactionType.REFUND
        ):
            refunded += transaction.amount

    remaining = (
        allocated
        - disbursed
        + refunded
    )

    return {
        "project_id": project_id,
        "allocated": round(allocated, 2),
        "disbursed": round(disbursed, 2),
        "utilized": round(utilized, 2),
        "refunded": round(refunded, 2),
        "remaining": round(
            max(remaining, 0),
            2,
        ),
    }

def list_project_funding_transactions(
    db: Session,
    project_id: int,
    current_user: User,
) -> list[ProjectFundingTransaction]:
    project = _get_project(
        db,
        project_id,
    )

    _check_project_access(
        project,
        current_user,
    )

    return (
        db.query(ProjectFundingTransaction)
        .filter(
            ProjectFundingTransaction.project_id == project_id
        )
        .order_by(
            ProjectFundingTransaction.created_at.desc()
        )
        .all()
    )