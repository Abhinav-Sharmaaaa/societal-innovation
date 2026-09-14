from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import (
    Challenge,
    ChallengeStatus,
)
from app.models.challenge_assignment import (
    AssignmentAction,
)
from app.models.challenge_review import (
    ChallengeReview,
    ReviewDecision,
)
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.services.authority_routing_service import (
    find_best_authority,
)
from app.services.challenge_assignment_service import (
    _create_assignment_transition,
)


# ============================================================
# Reviewer Authorization
# ============================================================

def _require_review_officer(
    reviewer: User,
) -> None:
    """
    Allow only users who are authorized to perform
    human-review decisions.
    """

    if reviewer.role not in {
        UserRole.REVIEW_OFFICER,
        UserRole.SUPER_ADMIN,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only REVIEW_OFFICER or SUPER_ADMIN users "
                "can review challenges."
            ),
        )


# ============================================================
# Challenge Review Eligibility
# ============================================================

def _get_reviewable_challenge(
    db: Session,
    challenge_id: int,
) -> Challenge:
    """
    Retrieve a challenge and ensure that it is currently
    waiting for human review.
    """

    challenge = db.get(
        Challenge,
        challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    if challenge.status != ChallengeStatus.UNDER_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This challenge is not currently awaiting "
                "human review."
            ),
        )

    return challenge


# ============================================================
# Reviewer Jurisdiction
# ============================================================

def _ensure_reviewer_scope(
    challenge: Challenge,
    reviewer: User,
) -> None:
    """
    Ensure that the reviewer is authorized to review the
    challenge based on the reviewer's organization scope.

    Rules:

    SUPER_ADMIN
        → unrestricted

    REVIEW_OFFICER with:
        state + district
            → district-scoped reviewer

        state only
            → state-scoped reviewer

        no organization
            → not allowed
    """

    # SUPER_ADMIN has platform-wide review authority.
    if reviewer.role == UserRole.SUPER_ADMIN:
        return

    # REVIEW_OFFICER must belong to an organization.
    if reviewer.organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Review officer is not associated with "
                "an organization."
            ),
        )

    organization = reviewer.organization

    # --------------------------------------------------------
    # State scope
    # --------------------------------------------------------

    if (
        organization.state
        and challenge.state
        and organization.state.strip().lower()
        != challenge.state.strip().lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Challenge is outside the reviewer's "
                "state jurisdiction."
            ),
        )

    # --------------------------------------------------------
    # District scope
    # --------------------------------------------------------

    if (
        organization.district
        and challenge.district
        and organization.district.strip().lower()
        != challenge.district.strip().lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Challenge is outside the reviewer's "
                "district jurisdiction."
            ),
        )


# ============================================================
# Authority Jurisdiction
# ============================================================

def _ensure_authority_matches_challenge(
    challenge: Challenge,
    authority: Organization,
) -> None:
    """
    Ensure that a reviewer cannot manually override the
    recommended authority with an authority outside the
    challenge's geographic jurisdiction.

    Current rules:
        State must match when both are available.
        District must match when both are available.

    A missing district on an authority is treated as a
    broader jurisdiction rather than an immediate mismatch.
    """

    # --------------------------------------------------------
    # State jurisdiction
    # --------------------------------------------------------

    if (
        challenge.state
        and authority.state
        and challenge.state.strip().lower()
        != authority.state.strip().lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected authority is outside the "
                "challenge state jurisdiction."
            ),
        )

    # --------------------------------------------------------
    # District jurisdiction
    # --------------------------------------------------------

    if (
        challenge.district
        and authority.district
        and challenge.district.strip().lower()
        != authority.district.strip().lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected authority is outside the "
                "challenge district jurisdiction."
            ),
        )


# ============================================================
# Review Queue
# ============================================================

def get_review_queue(
    db: Session,
    reviewer: User,
) -> list[Challenge]:
    """
    Return challenges currently waiting for human review.

    SUPER_ADMIN:
        receives the complete review queue.

    REVIEW_OFFICER:
        receives only challenges inside their geographic scope.
    """

    _require_review_officer(
        reviewer
    )

    statement = (
        select(Challenge)
        .where(
            Challenge.status
            == ChallengeStatus.UNDER_REVIEW
        )
        .order_by(
            Challenge.created_at.desc()
        )
    )

    challenges = list(
        db.scalars(statement).all()
    )

    # SUPER_ADMIN can see the entire platform queue.
    if reviewer.role == UserRole.SUPER_ADMIN:
        return challenges

    filtered: list[Challenge] = []

    for challenge in challenges:
        try:
            _ensure_reviewer_scope(
                challenge,
                reviewer,
            )
            filtered.append(challenge)

        except HTTPException:
            # A challenge outside the reviewer's scope is
            # simply omitted from their queue.
            continue

    return filtered


# ============================================================
# Accept AI Recommendation
# ============================================================

def accept_recommendation(
    db: Session,
    challenge_id: int,
    reviewer: User,
) -> Challenge:
    """
    Accept the current routing engine recommendation and
    assign the challenge to the recommended authority.

    The action is recorded as a HUMAN_ASSIGNED transition
    because a human reviewer made the final routing decision.
    """

    _require_review_officer(
        reviewer
    )

    challenge = _get_reviewable_challenge(
        db,
        challenge_id,
    )

    _ensure_reviewer_scope(
        challenge,
        reviewer,
    )

    # --------------------------------------------------------
    # Recalculate current authority recommendation
    # --------------------------------------------------------

    routing_result = find_best_authority(
        db=db,
        challenge=challenge,
    )

    if routing_result.recommended_authority_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No authority recommendation is available "
                "for this challenge."
            ),
        )

    # --------------------------------------------------------
    # Load recommended authority
    # --------------------------------------------------------

    authority = db.get(
        Organization,
        routing_result.recommended_authority_id,
    )

    if authority is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The recommended authority could not be found."
            ),
        )

    if not authority.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The recommended authority is no longer active."
            ),
        )

    # --------------------------------------------------------
    # Verify authority jurisdiction
    # --------------------------------------------------------

    _ensure_authority_matches_challenge(
        challenge,
        authority,
    )

    # --------------------------------------------------------
    # Record review decision
    # --------------------------------------------------------

    review = ChallengeReview(
        challenge_id=challenge.id,
        reviewer_id=reviewer.id,
        decision=ReviewDecision.ACCEPT_RECOMMENDATION,
        recommended_authority_id=authority.id,
        selected_authority_id=authority.id,
        reason=(
            "Reviewer accepted the current authority "
            "routing recommendation. "
            + routing_result.reason
        ),
    )

    db.add(review)

    # --------------------------------------------------------
    # Create assignment transition
    # --------------------------------------------------------

    result = _create_assignment_transition(
        db=db,
        challenge=challenge,
        authority=authority,
        performed_by=reviewer,
        action=AssignmentAction.HUMAN_ASSIGNED,
        reason=(
            f"Human reviewer {reviewer.full_name} accepted "
            f"the recommended authority {authority.name}. "
            f"Routing score: {routing_result.score:.1f}."
        ),
        remarks=None,
    )

    return result


# ============================================================
# Override Authority
# ============================================================

def override_authority(
    db: Session,
    challenge_id: int,
    reviewer: User,
    authority_id: int,
    reason: str,
) -> Challenge:
    """
    Allow an authorized reviewer to override the routing
    recommendation and select another authority.

    The selected authority must:
        - exist
        - be active
        - match the challenge geographic jurisdiction
    """

    _require_review_officer(
        reviewer
    )

    challenge = _get_reviewable_challenge(
        db,
        challenge_id,
    )

    _ensure_reviewer_scope(
        challenge,
        reviewer,
    )

    # --------------------------------------------------------
    # Load selected authority
    # --------------------------------------------------------

    authority = db.get(
        Organization,
        authority_id,
    )

    if authority is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected authority not found.",
        )

    if not authority.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected authority is inactive.",
        )

    # --------------------------------------------------------
    # Validate geographic jurisdiction
    # --------------------------------------------------------

    _ensure_authority_matches_challenge(
        challenge,
        authority,
    )

    # --------------------------------------------------------
    # Determine current recommendation
    # --------------------------------------------------------

    routing_result = find_best_authority(
        db=db,
        challenge=challenge,
    )

    recommended_authority_id = (
        routing_result.recommended_authority_id
    )

    # --------------------------------------------------------
    # Prevent meaningless override
    # --------------------------------------------------------

    if (
        recommended_authority_id is not None
        and authority.id == recommended_authority_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Selected authority is already the current "
                "routing recommendation. Use accept instead."
            ),
        )

    # --------------------------------------------------------
    # Record review decision
    # --------------------------------------------------------

    review = ChallengeReview(
        challenge_id=challenge.id,
        reviewer_id=reviewer.id,
        decision=ReviewDecision.OVERRIDE_AUTHORITY,
        recommended_authority_id=recommended_authority_id,
        selected_authority_id=authority.id,
        reason=reason,
    )

    db.add(review)

    # --------------------------------------------------------
    # Create assignment transition
    # --------------------------------------------------------

    result = _create_assignment_transition(
        db=db,
        challenge=challenge,
        authority=authority,
        performed_by=reviewer,
        action=AssignmentAction.HUMAN_ASSIGNED,
        reason=(
            f"Reviewer {reviewer.full_name} overrode the "
            f"AI/routing recommendation and selected "
            f"{authority.name}. "
            f"Reason: {reason}"
        ),
        remarks=None,
    )

    return result


# ============================================================
# Review History
# ============================================================

def get_review_history(
    db: Session,
    challenge_id: int,
    reviewer: User,
) -> list[ChallengeReview]:
    """
    Return human-review decisions for a challenge.

    A reviewer must be within the challenge's geographic
    scope to access its review history.
    """

    _require_review_officer(
        reviewer
    )

    challenge = db.get(
        Challenge,
        challenge_id,
    )

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found.",
        )

    _ensure_reviewer_scope(
        challenge,
        reviewer,
    )

    statement = (
        select(ChallengeReview)
        .where(
            ChallengeReview.challenge_id
            == challenge_id
        )
        .order_by(
            ChallengeReview.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )