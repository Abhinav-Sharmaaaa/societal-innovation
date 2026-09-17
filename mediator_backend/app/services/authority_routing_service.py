from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.models.organization import Organization
from app.models.organization_competency import OrganizationCompetency


# ============================================================
# Routing Result
# ============================================================

@dataclass
class AuthorityRoutingResult:
    recommended_authority_id: int | None
    recommended_authority_name: str | None
    score: float
    reason: str
    candidates: list[dict]


# ============================================================
# Normalization
# ============================================================

def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


# ============================================================
# Calculate Candidate Score
# ============================================================

def _calculate_score(
    challenge: Challenge,
    organization: Organization,
) -> tuple[float, list[str]]:

    reasons: list[str] = []
    score = 0.0

    challenge_state = _normalize(challenge.state)
    challenge_district = _normalize(challenge.district)
    challenge_locality = _normalize(challenge.locality)

    organization_state = _normalize(organization.state)
    organization_district = _normalize(organization.district)
    organization_locality = _normalize(
        organization.locality
    )

    # --------------------------------------------------------
    # Competency
    # --------------------------------------------------------

    category_match = any(
        competency.category == challenge.category
        for competency in organization.competencies
    )

    if not category_match:
        return 0.0, [
            "Organization does not have the required challenge competency."
        ]

    score += 60.0
    reasons.append(
        f"Organization is competent for {challenge.category.value}."
    )

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    if (
        challenge_state
        and organization_state
        and challenge_state == organization_state
    ):
        score += 15.0
        reasons.append("State jurisdiction matches.")

    # --------------------------------------------------------
    # District
    # --------------------------------------------------------

    if (
        challenge_district
        and organization_district
        and challenge_district == organization_district
    ):
        score += 20.0
        reasons.append("District jurisdiction matches.")

    # --------------------------------------------------------
    # Locality
    # --------------------------------------------------------

    if (
        challenge_locality
        and organization_locality
        and challenge_locality == organization_locality
    ):
        score += 5.0
        reasons.append("Locality jurisdiction matches.")

    return score, reasons


# ============================================================
# Find Best Authority
# ============================================================

def find_best_authority(
    db: Session,
    challenge: Challenge,
) -> AuthorityRoutingResult:

    organizations = list(
        db.scalars(
            select(Organization)
            .where(
                Organization.is_active.is_(True)
            )
            .order_by(Organization.name)
        ).unique().all()
    )

    candidates: list[dict] = []

    for organization in organizations:
        score, reasons = _calculate_score(
            challenge,
            organization,
        )

        if score <= 0:
            continue

        candidates.append(
            {
                "organization_id": organization.id,
                "organization_name": organization.name,
                "organization_type": (
                    organization.organization_type.value
                ),
                "score": score,
                "reason": " ".join(reasons),
            }
        )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if not candidates:
        return AuthorityRoutingResult(
            recommended_authority_id=None,
            recommended_authority_name=None,
            score=0.0,
            reason=(
                "No active authority matched both "
                "the challenge competency and available "
                "geographic jurisdiction."
            ),
            candidates=[],
        )

    best = candidates[0]

    return AuthorityRoutingResult(
        recommended_authority_id=best["organization_id"],
        recommended_authority_name=best["organization_name"],
        score=best["score"],
        reason=best["reason"],
        candidates=candidates,
    )