from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import (
    Challenge,
    ChallengeRoutingType,
    ChallengeStatus,
)
from app.models.challenge_assignment import (
    AssignmentAction,
    AssignmentStatus,
    ChallengeAssignment,
)
from app.models.organization import (
    Organization,
    OrganizationType,
)
from app.models.user import User
from app.services.authority_routing_service import (
    find_best_authority,
)


# ============================================================
# Internal Helpers
# ============================================================

def _get_challenge(
    db: Session,
    challenge_id: int,
) -> Challenge:
    challenge = db.get(
        Challenge,
        challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    return challenge


def _get_authority(
    db: Session,
    authority_id: int,
) -> Organization:
    authority = db.get(
        Organization,
        authority_id,
    )

    if authority is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authority organization not found.",
        )

    if not authority.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected authority is inactive.",
        )

    return authority


def _is_higher_authority(
    db: Session,
    current_authority_id: int,
    target_authority_id: int,
) -> bool:
    """Return True only when target is a strict ancestor of current."""

    if current_authority_id == target_authority_id:
        return False

    current = db.get(
        Organization,
        current_authority_id,
    )
    visited: set[int] = set()

    while current is not None:
        if current.id in visited:
            # Protect against a malformed hierarchy cycle.
            return False

        visited.add(current.id)

        parent_id = current.parent_organization_id
        if parent_id is None:
            return False

        if parent_id == target_authority_id:
            return True

        current = db.get(
            Organization,
            parent_id,
        )

    return False


def _get_active_assignment(
    db: Session,
    challenge_id: int,
) -> ChallengeAssignment | None:
    statement = (
        select(ChallengeAssignment)
        .where(
            ChallengeAssignment.challenge_id == challenge_id,
            ChallengeAssignment.status == AssignmentStatus.ACTIVE,
        )
        .order_by(
            ChallengeAssignment.created_at.desc()
        )
    )

    return db.scalars(statement).first()


# ============================================================
# RBAC Helpers
# ============================================================

def _is_super_admin(
    performed_by: User,
) -> bool:
    return performed_by.role.value == "SUPER_ADMIN"


def _is_official(
    performed_by: User,
) -> bool:
    return performed_by.role.value in {
        "MUNICIPALITY_OFFICER",
        "GOVERNMENT_OFFICER",
        "UNIVERSITY_ADMIN",
        "FACULTY",
        "STUDENT",
        "INDUSTRY_ADMIN",
        "INDUSTRY_MEMBER",
        "SUPER_ADMIN",
        "REVIEW_OFFICER",
    }


def _require_assignment_permission(
    performed_by: User,
) -> None:
    """
    Only authorized official accounts can perform
    authority assignment operations.

    Citizens are explicitly blocked.
    """

    if not _is_official(performed_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only authorized authority or administrative "
                "users can perform assignment operations."
            ),
        )


def _ensure_authorized_current_authority(
    challenge: Challenge,
    performed_by: User,
) -> None:
    """
    Only the current authority's authorized officer or
    SUPER_ADMIN can modify the current assignment.
    """

    if _is_super_admin(performed_by):
        return

    if challenge.current_authority_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge has no current authority.",
        )

    if performed_by.organization_id != challenge.current_authority_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You are not authorized to modify the "
                "assignment of this challenge."
            ),
        )


# ============================================================
# Routing Type
# ============================================================

def _set_routing_type(
    challenge: Challenge,
    authority: Organization,
) -> None:
    """
    Synchronize challenge routing type with the receiving
    organization.
    """

    if authority.organization_type == OrganizationType.MUNICIPALITY:
        challenge.routing_type = (
            ChallengeRoutingType.MUNICIPALITY
        )

    elif (
        authority.organization_type
        == OrganizationType.GOVERNMENT_DEPARTMENT
    ):
        challenge.routing_type = (
            ChallengeRoutingType.GOVERNMENT
        )

    elif authority.organization_type in {
        OrganizationType.UNIVERSITY,
        OrganizationType.INDUSTRY,
    }:
        challenge.routing_type = (
            ChallengeRoutingType.INNOVATION
        )


# ============================================================
# Assignment Transition
# ============================================================

def _create_assignment_transition(
    db: Session,
    challenge: Challenge,
    authority: Organization,
    performed_by: User,
    action: AssignmentAction,
    reason: str,
    remarks: str | None,
) -> Challenge:
    """
    Complete an authority transition and create an immutable
    assignment-history record.
    """

    now = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # Close previous active assignment
    # --------------------------------------------------------

    previous_assignment = _get_active_assignment(
        db,
        challenge.id,
    )

    if previous_assignment is not None:
        previous_assignment.status = (
            AssignmentStatus.COMPLETED
        )
        previous_assignment.completed_at = now

    previous_authority_id = (
        challenge.current_authority_id
    )

    # --------------------------------------------------------
    # Create history record
    # --------------------------------------------------------

    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        from_authority_id=previous_authority_id,
        to_authority_id=authority.id,
        performed_by=performed_by.id,
        action=action,
        status=AssignmentStatus.ACTIVE,
        reason=reason,
        remarks=remarks,
    )

    db.add(assignment)

    # --------------------------------------------------------
    # Update challenge
    # --------------------------------------------------------

    challenge.current_authority_id = authority.id
    challenge.assigned_by = performed_by.id
    challenge.assigned_at = now
    challenge.status = ChallengeStatus.ROUTED

    _set_routing_type(
        challenge,
        authority,
    )

    challenge.routing_reason = reason

    db.commit()
    db.refresh(challenge)

    return challenge


# ============================================================
# Initial Human Assignment
# ============================================================

def assign_challenge(
    db: Session,
    challenge_id: int,
    authority_id: int,
    performed_by: User,
    remarks: str | None = None,
) -> Challenge:
    """
    Assign a challenge after human review.

    Citizens are not allowed to perform this operation.
    """

    _require_assignment_permission(
        performed_by
    )

    challenge = _get_challenge(
        db,
        challenge_id,
    )

    authority = _get_authority(
        db,
        authority_id,
    )

    if challenge.current_authority_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Challenge already has a current authority. "
                "Use reassign or escalate instead."
            ),
        )

    reason = (
        f"Challenge assigned to {authority.name} by "
        f"{performed_by.full_name}."
    )

    return _create_assignment_transition(
        db=db,
        challenge=challenge,
        authority=authority,
        performed_by=performed_by,
        action=AssignmentAction.HUMAN_ASSIGNED,
        reason=reason,
        remarks=remarks,
    )


# ============================================================
# Automatic Routing From Recommendation
# ============================================================

def auto_route_challenge(
    db: Session,
    challenge_id: int,
    performed_by: User,
    remarks: str | None = None,
) -> Challenge:
    """
    Calculate an authority recommendation and assign the
    challenge when the routing policy allows automatic routing.

    The user triggering this operation must be an authorized
    official/admin. The system still records that user as the
    actor in the audit trail.
    """

    _require_assignment_permission(
        performed_by
    )

    challenge = _get_challenge(
        db,
        challenge_id,
    )

    # --------------------------------------------------------
    # Existing assignment protection
    # --------------------------------------------------------

    if challenge.current_authority_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Challenge already has a current authority. "
                "Use reassign or escalate instead."
            ),
        )

    # --------------------------------------------------------
    # AI review protection
    # --------------------------------------------------------

    if (
        challenge.ai_requires_human_review is True
        or challenge.ai_innovation_requires_human_review is True
        or challenge.ai_innovation_type_requires_human_review is True
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Challenge requires human review before "
                "automatic authority routing."
            ),
        )

    # --------------------------------------------------------
    # Calculate recommendation
    # --------------------------------------------------------

    routing_result = find_best_authority(
        db=db,
        challenge=challenge,
    )

    if routing_result.recommended_authority_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No suitable authority was found for "
                "automatic routing."
            ),
        )

    # --------------------------------------------------------
    # Routing confidence policy
    # --------------------------------------------------------

    if routing_result.score < 85.0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Authority match is not strong enough for "
                "automatic routing. Human review is required."
            ),
        )

    authority = _get_authority(
        db,
        routing_result.recommended_authority_id,
    )

    reason = (
        "Automatically routed to "
        f"{authority.name}. "
        f"Routing score: {routing_result.score:.1f}. "
        f"Reason: {routing_result.reason}"
    )

    return _create_assignment_transition(
        db=db,
        challenge=challenge,
        authority=authority,
        performed_by=performed_by,
        action=AssignmentAction.AUTO_ASSIGNED,
        reason=reason,
        remarks=remarks,
    )


# ============================================================
# Reassign
# ============================================================

def reassign_challenge(
    db: Session,
    challenge_id: int,
    authority_id: int,
    performed_by: User,
    reason: str,
    remarks: str | None = None,
) -> Challenge:
    """
    Transfer a challenge from the current authority to
    another authority.
    """

    _require_assignment_permission(
        performed_by
    )

    challenge = _get_challenge(
        db,
        challenge_id,
    )

    _ensure_authorized_current_authority(
        challenge,
        performed_by,
    )

    authority = _get_authority(
        db,
        authority_id,
    )

    if challenge.current_authority_id == authority.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Challenge is already assigned to this authority."
            ),
        )

    return _create_assignment_transition(
        db=db,
        challenge=challenge,
        authority=authority,
        performed_by=performed_by,
        action=AssignmentAction.REASSIGNED,
        reason=reason,
        remarks=remarks,
    )


# ============================================================
# Escalate
# ============================================================

def escalate_challenge(
    db: Session,
    challenge_id: int,
    authority_id: int,
    performed_by: User,
    reason: str,
    remarks: str | None = None,
) -> Challenge:
    """
    Escalate a challenge from the current authority to another
    authority because the current authority cannot resolve it.

    Hierarchical validation will be added after the authority
    hierarchy is populated.
    """

    _require_assignment_permission(
        performed_by
    )

    challenge = _get_challenge(
        db,
        challenge_id,
    )

    _ensure_authorized_current_authority(
        challenge,
        performed_by,
    )

    authority = _get_authority(
        db,
        authority_id,
    )

    if challenge.current_authority_id == authority.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Challenge is already assigned to this authority."
            ),
        )

    if (
        challenge.current_authority_id is None
        or not _is_higher_authority(
            db=db,
            current_authority_id=challenge.current_authority_id,
            target_authority_id=authority.id,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Escalation target must be a higher-level authority "
                "in the current authority hierarchy."
            ),
        )

    escalation_reason = (
        f"Challenge escalated from authority "
        f"{challenge.current_authority_id} to "
        f"{authority.id}. Reason: {reason}"
    )

    return _create_assignment_transition(
        db=db,
        challenge=challenge,
        authority=authority,
        performed_by=performed_by,
        action=AssignmentAction.ESCALATED,
        reason=escalation_reason,
        remarks=remarks,
    )


# ============================================================
# Assignment History
# ============================================================

def get_assignment_history(
    db: Session,
    challenge_id: int,
) -> list[ChallengeAssignment]:

    _get_challenge(
        db,
        challenge_id,
    )

    statement = (
        select(ChallengeAssignment)
        .where(
            ChallengeAssignment.challenge_id == challenge_id,
        )
        .order_by(
            ChallengeAssignment.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )

# ============================================================
# Transfer Authority Options
# ============================================================

def get_transfer_authorities(
    db: Session,
    challenge_id: int,
    performed_by: User,
) -> dict:
    """
    Return valid authority destinations for transferring a
    currently assigned challenge.

    Destinations are limited to active municipality and
    government-department authorities in the same state and
    district as the current authority.

    The current authority itself is excluded.
    """

    _require_assignment_permission(performed_by)

    challenge = _get_challenge(
        db,
        challenge_id,
    )

    _ensure_authorized_current_authority(
        challenge,
        performed_by,
    )

    if challenge.current_authority_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Challenge has no current authority.",
        )

    current_authority = _get_authority(
        db,
        challenge.current_authority_id,
    )

    statement = (
        select(Organization)
        .where(
            Organization.is_active.is_(True),
            Organization.organization_type.in_(
                {
                    OrganizationType.MUNICIPALITY,
                    OrganizationType.GOVERNMENT_DEPARTMENT,
                }
            ),
            Organization.id != current_authority.id,
            Organization.state == current_authority.state,
            Organization.district == current_authority.district,
        )
        .order_by(Organization.name)
    )

    authorities = list(
        db.scalars(statement).all()
    )

    return {
        "current_authority_id": current_authority.id,
        "current_authority_name": current_authority.name,
        "authorities": [
            {
                "id": authority.id,
                "name": authority.name,
                "organization_type": (
                    authority.organization_type.value
                    if hasattr(
                        authority.organization_type,
                        "value",
                    )
                    else str(authority.organization_type)
                ),
                "state": authority.state,
                "district": authority.district,
                "parent_organization_id": (
                    authority.parent_organization_id
                ),
            }
            for authority in authorities
        ],
    }