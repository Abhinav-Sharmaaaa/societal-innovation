from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.organization import Organization, OrganizationType
from app.models.reputation import (
    ReputationEntityType,
    ReputationEvent,
    ReputationEventType,
)
from app.models.reputation_score import (
    ReputationScore,
    ReputationScoreEntityType,
)
from app.models.user import User


# ============================================================
# REPUTATION POINT CONFIGURATION
# ============================================================

POINT_VALUES = {
    ReputationEventType.CHALLENGE_SUBMITTED: 5,
    ReputationEventType.CHALLENGE_VALIDATED: 15,
    ReputationEventType.UNIVERSITY_PROPOSAL: 20,
    ReputationEventType.PROJECT_CONTRIBUTION: 15,
    ReputationEventType.MILESTONE_COMPLETED: 10,
    ReputationEventType.DELIVERABLE_APPROVED: 10,
    ReputationEventType.FUNDING_CONTRIBUTION: 25,
    ReputationEventType.PROJECT_COMPLETED: 50,
    ReputationEventType.POSITIVE_PROJECT_OUTCOME: 75,
}


# ============================================================
# HELPERS
# ============================================================

def _get_user(
    db: Session,
    user_id: int,
) -> User:
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


def _get_organization(
    db: Session,
    organization_id: int,
) -> Organization:
    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    return organization


def _get_or_create_user_score(
    db: Session,
    user_id: int,
) -> ReputationScore:

    score = (
        db.query(ReputationScore)
        .filter(
            ReputationScore.entity_type
            == ReputationScoreEntityType.CITIZEN,
            ReputationScore.user_id == user_id,
            ReputationScore.organization_id.is_(None),
        )
        .first()
    )

    if score:
        return score

    score = ReputationScore(
        entity_type=ReputationScoreEntityType.CITIZEN,
        user_id=user_id,
        organization_id=None,
        total_points=0,
        contribution_count=0,
    )

    db.add(score)
    db.flush()

    return score


def _get_or_create_organization_score(
    db: Session,
    organization: Organization,
) -> tuple[
    ReputationScore,
    ReputationEntityType,
    ReputationScoreEntityType,
]:

    organization_type = organization.organization_type

    if organization_type == OrganizationType.UNIVERSITY:
        event_entity_type = ReputationEntityType.UNIVERSITY
        score_entity_type = ReputationScoreEntityType.UNIVERSITY

    elif organization_type == OrganizationType.INDUSTRY:
        event_entity_type = ReputationEntityType.INDUSTRY
        score_entity_type = ReputationScoreEntityType.INDUSTRY

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Reputation scoring is currently supported only "
                "for UNIVERSITY and INDUSTRY organizations."
            ),
        )

    score = (
        db.query(ReputationScore)
        .filter(
            ReputationScore.entity_type == score_entity_type,
            ReputationScore.organization_id == organization.id,
            ReputationScore.user_id.is_(None),
        )
        .first()
    )

    if not score:
        score = ReputationScore(
            entity_type=score_entity_type,
            user_id=None,
            organization_id=organization.id,
            total_points=0,
            contribution_count=0,
        )

        db.add(score)
        db.flush()

    return (
        score,
        event_entity_type,
        score_entity_type,
    )


def _find_existing_event(
    db: Session,
    event_type: ReputationEventType,
    description: str,
    user_id: int | None,
    organization_id: int | None,
    project_id: int | None,
) -> ReputationEvent | None:

    query = db.query(ReputationEvent).filter(
        ReputationEvent.event_type == event_type,
        ReputationEvent.description == description,
    )

    if user_id is not None:
        query = query.filter(
            ReputationEvent.user_id == user_id,
            ReputationEvent.organization_id.is_(None),
        )

    else:
        query = query.filter(
            ReputationEvent.organization_id == organization_id,
            ReputationEvent.user_id.is_(None),
        )

    if project_id is not None:
        query = query.filter(
            ReputationEvent.project_id == project_id
        )
    else:
        query = query.filter(
            ReputationEvent.project_id.is_(None)
        )

    return query.first()


# ============================================================
# AWARD REPUTATION
# ============================================================

def award_reputation_points(
    db: Session,
    event_type: ReputationEventType,
    description: str,
    user_id: int | None = None,
    organization_id: int | None = None,
    project_id: int | None = None,
) -> ReputationEvent:

    # --------------------------------------------------------
    # Validate target
    # --------------------------------------------------------

    if user_id is None and organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either user_id or organization_id must be provided.",
        )

    if user_id is not None and organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either user_id or organization_id, not both.",
        )

    # --------------------------------------------------------
    # Validate event type / points
    # --------------------------------------------------------

    points = POINT_VALUES.get(event_type)

    if points is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No point value configured for this reputation event.",
        )

    # --------------------------------------------------------
    # Idempotency protection
    #
    # The same business event should not award the same
    # reputation points twice.
    #
    # For integrations, make `description` unique per source
    # event, e.g.
    #
    # "Milestone completed: milestone_id=12"
    # "Deliverable approved: deliverable_id=7"
    # "Funding completed: transaction_id=9"
    # --------------------------------------------------------

    existing_event = _find_existing_event(
        db=db,
        event_type=event_type,
        description=description,
        user_id=user_id,
        organization_id=organization_id,
        project_id=project_id,
    )

    if existing_event:
        return existing_event

    # --------------------------------------------------------
    # User-level reputation
    # --------------------------------------------------------

    if user_id is not None:

        user = _get_user(
            db=db,
            user_id=user_id,
        )

        # Current design only maintains user-level reputation
        # for citizens.
        #
        # University / industry reputation is organization-level.

        if user.role.value != "CITIZEN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "User-level reputation is currently supported "
                    "only for CITIZEN users."
                ),
            )

        entity_type = ReputationEntityType.CITIZEN

        score = _get_or_create_user_score(
            db=db,
            user_id=user_id,
        )

    # --------------------------------------------------------
    # Organization-level reputation
    # --------------------------------------------------------

    else:

        organization = _get_organization(
            db=db,
            organization_id=organization_id,
        )

        (
            score,
            entity_type,
            _score_entity_type,
        ) = _get_or_create_organization_score(
            db=db,
            organization=organization,
        )

    # --------------------------------------------------------
    # Create immutable reputation event
    # --------------------------------------------------------

    event = ReputationEvent(
        entity_type=entity_type,
        user_id=user_id,
        organization_id=organization_id,
        event_type=event_type,
        points=points,
        description=description,
        project_id=project_id,
    )

    db.add(event)

    # --------------------------------------------------------
    # Update aggregate score
    # --------------------------------------------------------

    score.total_points += points
    score.contribution_count += 1

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# READ USER REPUTATION
# ============================================================

def get_user_reputation(
    db: Session,
    user_id: int,
) -> ReputationScore | None:

    return (
        db.query(ReputationScore)
        .filter(
            ReputationScore.user_id == user_id,
            ReputationScore.entity_type
            == ReputationScoreEntityType.CITIZEN,
            ReputationScore.organization_id.is_(None),
        )
        .first()
    )


# ============================================================
# READ ORGANIZATION REPUTATION
# ============================================================

def get_organization_reputation(
    db: Session,
    organization_id: int,
) -> ReputationScore | None:

    return (
        db.query(ReputationScore)
        .filter(
            ReputationScore.organization_id == organization_id,
            ReputationScore.user_id.is_(None),
        )
        .first()
    )


# ============================================================
# REPUTATION HISTORY
# ============================================================

def get_reputation_history(
    db: Session,
    user_id: int | None = None,
    organization_id: int | None = None,
) -> list[ReputationEvent]:

    if user_id is None and organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide user_id or organization_id.",
        )

    if user_id is not None and organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either user_id or organization_id, not both.",
        )

    query = db.query(ReputationEvent)

    if user_id is not None:
        query = query.filter(
            ReputationEvent.user_id == user_id
        )

    else:
        query = query.filter(
            ReputationEvent.organization_id == organization_id
        )

    return (
        query
        .order_by(
            ReputationEvent.created_at.desc()
        )
        .all()
    )