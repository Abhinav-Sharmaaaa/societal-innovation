from __future__ import annotations

import re
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.models.organization import (
    Organization,
    OrganizationType,
)
from app.models.organization_capability import (
    OrganizationCapability,
)
from app.models.rfp import RFP
from app.ai.matching_schemas import (
    UniversityMatchRecommendation,
    UniversityMatchingResponse,
)


# ============================================================
# Scoring Weights
# ============================================================

COMPETENCY_WEIGHT = 35.0
CAPABILITY_WEIGHT = 40.0
TEXT_WEIGHT = 15.0
LOCATION_WEIGHT = 10.0


# ============================================================
# Text Helpers
# ============================================================

STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "their",
    "will",
    "using",
    "used",
    "are",
    "was",
    "were",
    "has",
    "have",
    "been",
    "can",
    "may",
    "also",
    "its",
    "our",
    "your",
    "need",
    "needs",
    "solution",
    "problem",
}


def _tokenize(text: str | None) -> set[str]:
    if not text:
        return set()

    tokens = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        token
        for token in tokens
        if len(token) >= 3
        and token not in STOP_WORDS
    }


def _safe_overlap_score(
    source_tokens: set[str],
    target_tokens: set[str],
) -> float:
    if not source_tokens or not target_tokens:
        return 0.0

    intersection = (
        source_tokens & target_tokens
    )

    if not intersection:
        return 0.0

    # Jaccard-like relevance score.
    union = source_tokens | target_tokens

    return (
        len(intersection)
        / len(union)
        * 100.0
    )


def _contains_relevant_term(
    challenge_tokens: set[str],
    capability_text: str,
) -> bool:
    capability_tokens = _tokenize(
        capability_text
    )

    return bool(
        challenge_tokens
        & capability_tokens
    )


# ============================================================
# Build Matching Text
# ============================================================

def _build_rfp_text(
    rfp: RFP,
    challenge: Challenge,
) -> str:
    parts = [
        rfp.title,
        rfp.description,
        rfp.objectives,
        rfp.technical_requirements,
        rfp.expected_outcomes,
        challenge.title,
        challenge.description,
        challenge.address,
        challenge.district,
        challenge.state,
    ]

    return " ".join(
        part
        for part in parts
        if part
    )


# ============================================================
# Match One University
# ============================================================

def _score_university(
    rfp: RFP,
    challenge: Challenge,
    university: Organization,
    capabilities: list[OrganizationCapability],
) -> UniversityMatchRecommendation:

    # --------------------------------------------------------
    # Competency score
    # --------------------------------------------------------

    matched_competencies: list[str] = []

    for competency in university.competencies:
        if competency.category == challenge.category:
            matched_competencies.append(
                competency.category.value
            )

    competency_score = (
        100.0
        if matched_competencies
        else 0.0
    )

    # --------------------------------------------------------
    # RFP / challenge text
    # --------------------------------------------------------

    matching_text = _build_rfp_text(
        rfp,
        challenge,
    )

    problem_tokens = _tokenize(
        matching_text
    )

    # --------------------------------------------------------
    # Capability scoring
    # --------------------------------------------------------

    matched_capabilities: list[str] = []

    capability_scores: list[float] = []

    for capability in capabilities:

        capability_text = " ".join(
            part
            for part in [
                capability.name,
                capability.description,
            ]
            if part
        )

        capability_tokens = _tokenize(
            capability_text
        )

        score = _safe_overlap_score(
            problem_tokens,
            capability_tokens,
        )

        capability_scores.append(score)

        if (
            score >= 5.0
            or _contains_relevant_term(
                problem_tokens,
                capability_text,
            )
        ):
            matched_capabilities.append(
                capability.name
            )

    capability_score = (
        max(capability_scores)
        if capability_scores
        else 0.0
    )

    # --------------------------------------------------------
    # Aggregate capability text relevance
    # --------------------------------------------------------

    all_capability_text = " ".join(
        " ".join(
            part
            for part in [
                capability.name,
                capability.description,
            ]
            if part
        )
        for capability in capabilities
    )

    text_relevance_score = (
        _safe_overlap_score(
            problem_tokens,
            _tokenize(
                all_capability_text
            ),
        )
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    location_score = 0.0

    if (
        challenge.state
        and university.state
        and challenge.state.lower()
        == university.state.lower()
    ):
        location_score += 70.0

    if (
        challenge.district
        and university.district
        and challenge.district.lower()
        == university.district.lower()
    ):
        location_score += 30.0

    location_score = min(
        location_score,
        100.0,
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    final_score = (
        competency_score
        * COMPETENCY_WEIGHT
        / 100.0
        +
        capability_score
        * CAPABILITY_WEIGHT
        / 100.0
        +
        text_relevance_score
        * TEXT_WEIGHT
        / 100.0
        +
        location_score
        * LOCATION_WEIGHT
        / 100.0
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation_parts: list[str] = []

    if matched_competencies:
        explanation_parts.append(
            "The university matches the "
            f"challenge competency: "
            f"{', '.join(matched_competencies)}."
        )

    if matched_capabilities:
        explanation_parts.append(
            "Relevant capabilities include: "
            f"{', '.join(matched_capabilities[:5])}."
        )

    if location_score > 0:
        explanation_parts.append(
            "The university has compatible "
            "geographic coverage."
        )

    if not explanation_parts:
        explanation_parts.append(
            "The university was retained based "
            "on its available capability profile."
        )

    return UniversityMatchRecommendation(
        rank=1,
        organization_id=university.id,
        organization_name=university.name,
        score=round(
            min(final_score, 100.0),
            2,
        ),
        competency_match_score=round(
            competency_score,
            2,
        ),
        capability_match_score=round(
            capability_score,
            2,
        ),
        text_relevance_score=round(
            text_relevance_score,
            2,
        ),
        location_score=round(
            location_score,
            2,
        ),
        matched_competencies=matched_competencies,
        matched_capabilities=matched_capabilities,
        explanation=" ".join(
            explanation_parts
        ),
    )


# ============================================================
# Match Universities
# ============================================================

def match_universities_for_rfp(
    db: Session,
    rfp_id: int,
) -> UniversityMatchingResponse:

    # --------------------------------------------------------
    # RFP
    # --------------------------------------------------------

    rfp = db.get(
        RFP,
        rfp_id,
    )

    if rfp is None:
        raise ValueError(
            "RFP not found."
        )

    # --------------------------------------------------------
    # Innovation Opportunity / Challenge
    # --------------------------------------------------------

    opportunity = (
        rfp.innovation_opportunity
    )

    if opportunity is None:
        raise ValueError(
            "RFP is not linked to an innovation opportunity."
        )

    challenge = opportunity.challenge

    if challenge is None:
        raise ValueError(
            "Innovation opportunity is not linked "
            "to a challenge."
        )

    # --------------------------------------------------------
    # Candidate universities
    # --------------------------------------------------------

    universities = list(
        db.scalars(
            select(Organization)
            .where(
                Organization.organization_type
                == OrganizationType.UNIVERSITY,
                Organization.is_active.is_(True),
            )
        ).all()
    )

    recommendations: list[
        UniversityMatchRecommendation
    ] = []

    for university in universities:

        capabilities = list(
            db.scalars(
                select(
                    OrganizationCapability
                ).where(
                    OrganizationCapability.organization_id
                    == university.id
                )
            ).all()
        )

        recommendation = _score_university(
            rfp=rfp,
            challenge=challenge,
            university=university,
            capabilities=capabilities,
        )

        recommendations.append(
            recommendation
        )

    # --------------------------------------------------------
    # Rank
    # --------------------------------------------------------

    recommendations.sort(
        key=lambda item: item.score,
        reverse=True,
    )

    top_three = recommendations[:3]

    for index, recommendation in enumerate(
        top_three,
        start=1,
    ):
        recommendation.rank = index

    return UniversityMatchingResponse(
        rfp_id=rfp.id,
        challenge_id=challenge.id,
        recommendations=top_three,
        total_candidates_evaluated=len(
            universities
        ),
    )