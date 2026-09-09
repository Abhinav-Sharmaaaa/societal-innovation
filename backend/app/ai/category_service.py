from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "category"
    / "controlled_baselines"
    / "B_text_plus_location.joblib"
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_VERSION = "category-tfidf-logreg-v1"

# Initial empirical review policy.
# These values were derived from the current geographic
# holdout analysis and should remain configurable.
CONFIDENCE_THRESHOLD = 0.50
MARGIN_THRESHOLD = 0.20


# ============================================================
# MODEL LOADING
# ============================================================

_model: Any | None = None


def get_model() -> Any:
    """
    Load the trained category model once and reuse it.
    """

    global _model

    if _model is None:
        if not MODEL_FILE.exists():
            raise FileNotFoundError(
                f"Category model not found:\n{MODEL_FILE}"
            )

        _model = joblib.load(MODEL_FILE)

    return _model


# ============================================================
# INPUT REPRESENTATION
# ============================================================

def _clean(value: str | None) -> str:
    if value is None:
        return ""

    return str(value).strip()


def build_category_text(
    *,
    description: str,
    problem_context: str = "",
    citizen_statement: str = "",
    state: str = "",
    district: str = "",
) -> str:
    """
    Build the exact input representation used by the winning
    B_text_plus_location model.

    Training representation:
      description
      problem_context
      citizen_statement
      state
      district

    Title and language are intentionally excluded.
    """

    parts = [
        f"Description: {_clean(description)}",
        f"Context: {_clean(problem_context)}",
        f"Citizen statement: {_clean(citizen_statement)}",
        f"State: {_clean(state)}",
        f"District: {_clean(district)}",
    ]

    return "\n".join(
        part
        for part in parts
        if part.split(":", 1)[-1].strip()
    )


# ============================================================
# PREDICTION
# ============================================================

def predict_category(
    *,
    description: str,
    problem_context: str = "",
    citizen_statement: str = "",
    state: str = "",
    district: str = "",
) -> dict[str, Any]:
    """
    Predict the primary societal category and return:

      - top-3 categories
      - top-1 confidence
      - top-2 confidence
      - top-1/top-2 margin
      - automatic classification vs human review

    The service does NOT mutate the challenge or database.
    """

    description = _clean(description)

    if not description:
        raise ValueError(
            "description is required for category prediction."
        )

    model = get_model()

    text = build_category_text(
        description=description,
        problem_context=problem_context,
        citizen_statement=citizen_statement,
        state=state,
        district=district,
    )

    probabilities = model.predict_proba([text])[0]
    classes = np.asarray(model.classes_)

    sorted_indices = np.argsort(
        probabilities
    )[::-1]

    top1_index = int(sorted_indices[0])
    top2_index = int(sorted_indices[1])

    top1_category = str(classes[top1_index])
    top2_category = str(classes[top2_index])

    top1_probability = float(
        probabilities[top1_index]
    )

    top2_probability = float(
        probabilities[top2_index]
    )

    margin = float(
        top1_probability - top2_probability
    )

    top3 = []

    for rank, index in enumerate(
        sorted_indices[:3],
        start=1,
    ):
        top3.append(
            {
                "rank": rank,
                "category": str(classes[index]),
                "confidence": float(probabilities[index]),
            }
        )

    requires_human_review = (
        top1_probability < CONFIDENCE_THRESHOLD
        or margin < MARGIN_THRESHOLD
    )

    decision = (
        "HUMAN_REVIEW"
        if requires_human_review
        else "AUTO_CLASSIFY"
    )

    return {
        "category": top1_category,
        "confidence": round(
            top1_probability,
            6,
        ),
        "second_category": top2_category,
        "second_confidence": round(
            top2_probability,
            6,
        ),
        "margin": round(
            margin,
            6,
        ),
        "top_3": top3,
        "decision": decision,
        "requires_human_review": requires_human_review,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "margin_threshold": MARGIN_THRESHOLD,
        "model_version": MODEL_VERSION,
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_category_model_info() -> dict[str, Any]:
    """
    Return basic information useful for health/debug endpoints.
    """

    model = get_model()

    classes = [
        str(value)
        for value in model.classes_
    ]

    return {
        "model_version": MODEL_VERSION,
        "model_type": "TF-IDF + Logistic Regression",
        "model_file": str(MODEL_FILE),
        "classes": classes,
        "class_count": len(classes),
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "margin_threshold": MARGIN_THRESHOLD,
    }