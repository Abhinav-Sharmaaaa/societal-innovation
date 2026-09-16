"""
Duplicate-check service.

Finds existing challenges that are similar to a new submission
based on two independent signals:

  1. **Location proximity** – same district (or state if district
     is absent). This is the primary geo-filter.

  2. **Category match** – same challenge category is a strong
     signal that two reports describe the same underlying issue.

  3. **Title / description similarity** – simple normalised
     keyword overlap (no ML dependency, works offline).

A similarity score between 0.0 and 1.0 is computed for each
candidate.  Candidates scoring >= SIMILARITY_THRESHOLD are
returned, sorted by descending score.
"""

from __future__ import annotations

import re
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge, ChallengeStatus


# ============================================================
# Constants
# ============================================================

SIMILARITY_THRESHOLD = 0.35   # Minimum score to flag as duplicate
MAX_RESULTS = 5                # Maximum duplicates returned

# Statuses that disqualify a challenge from being a duplicate
# (e.g. REJECTED challenges should not block new submissions)
EXCLUDED_STATUSES: set[ChallengeStatus] = {
    ChallengeStatus.REJECTED,
    ChallengeStatus.CLOSED,
}


# ============================================================
# Text normalisation helpers
# ============================================================

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "in", "on", "at", "of", "to",
    "and", "or", "for", "with", "this", "that", "are", "was",
    "has", "have", "be", "been", "by", "from", "it", "its",
    "not", "no", "as", "se", "ki", "ka", "ke", "hai", "mein",
})


def _tokenise(text: str) -> set[str]:
    """Lower-case, strip punctuation, remove stop-words."""
    tokens = re.findall(r"[a-z\u0900-\u097f]+", text.lower())
    return {t for t in tokens if t not in _STOP_WORDS and len(t) > 2}


def _jaccard(set_a: set[str], set_b: set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# ============================================================
# Scoring
# ============================================================

def _score(
    candidate: Challenge,
    *,
    title: str,
    description: str,
    category: str | None,
    district: str | None,
    state: str | None,
) -> float:
    """
    Return a similarity score in [0, 1].

    Weights:
      - Location (district / state match): 0.40
      - Category match:                    0.30
      - Text similarity (title + desc):    0.30
    """

    score = 0.0

    # ---- Location (0.40) ----
    cand_district = (candidate.district or "").strip().lower()
    cand_state    = (candidate.state    or "").strip().lower()
    inp_district  = (district or "").strip().lower()
    inp_state     = (state    or "").strip().lower()

    if inp_district and cand_district:
        if inp_district == cand_district:
            score += 0.40          # exact district match
    elif inp_state and cand_state:
        if inp_state == cand_state:
            score += 0.20          # same state, unknown district

    # ---- Category (0.30) ----
    if category and candidate.category:
        if category.upper() == candidate.category.upper():
            score += 0.30

    # ---- Text (0.30) ----
    inp_tokens = (
        _tokenise(title) | _tokenise(description)
    )

    cand_tokens = (
        _tokenise(candidate.title)
        | _tokenise(candidate.description or "")
    )

    text_sim = _jaccard(inp_tokens, cand_tokens)
    score += text_sim * 0.30

    return round(min(score, 1.0), 4)


# ============================================================
# Public entry point
# ============================================================

def find_duplicates(
    db: Session,
    *,
    title: str,
    description: str,
    category: str | None,
    district: str | None,
    state: str | None,
) -> list[dict]:
    """
    Return a ranked list of likely-duplicate challenges.

    Each item in the returned list contains:
      - id, title, description (truncated), category,
        status, district, state, similarity_score
    """

    # ---- Geo-filter: same district OR same state ----
    stmt = select(Challenge)

    if district:
        stmt = stmt.where(
            Challenge.district.ilike(f"%{district.strip()}%")
        )
    elif state:
        stmt = stmt.where(
            Challenge.state.ilike(f"%{state.strip()}%")
        )
    # No location at all → scan everything (rare; still useful)

    candidates: Sequence[Challenge] = db.scalars(stmt).all()

    results = []

    for challenge in candidates:
        if challenge.status in EXCLUDED_STATUSES:
            continue

        sim = _score(
            challenge,
            title=title,
            description=description,
            category=category,
            district=district,
            state=state,
        )

        if sim >= SIMILARITY_THRESHOLD:
            desc_preview = (challenge.description or "")[:200]

            results.append({
                "id":               challenge.id,
                "title":            challenge.title,
                "description":      desc_preview,
                "category":         challenge.category,
                "status":           challenge.status,
                "district":         challenge.district,
                "state":            challenge.state,
                "similarity_score": sim,
            })

    results.sort(
        key=lambda r: r["similarity_score"],
        reverse=True,
    )

    return results[:MAX_RESULTS]
