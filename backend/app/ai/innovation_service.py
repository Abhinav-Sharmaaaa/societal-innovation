from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INNOVATION_REQUIRED_MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "innovation"
    / "innovation_required_tfidf_logreg.joblib"
)

INNOVATION_TYPE_MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "innovation"
    / "innovation_type_tfidf_logreg.joblib"
)


REQUIRED_CONFIDENCE_THRESHOLD = 0.70
TYPE_CONFIDENCE_THRESHOLD = 0.70
TYPE_MARGIN_THRESHOLD = 0.40


_REQUIRED_MODEL = None
_TYPE_MODEL = None


def _load_required_model():
    global _REQUIRED_MODEL

    if _REQUIRED_MODEL is None:
        if not INNOVATION_REQUIRED_MODEL_PATH.exists():
            raise FileNotFoundError(
                "Innovation-required model not found:\n"
                f"{INNOVATION_REQUIRED_MODEL_PATH}"
            )

        _REQUIRED_MODEL = joblib.load(
            INNOVATION_REQUIRED_MODEL_PATH
        )

    return _REQUIRED_MODEL


def _load_type_model():
    global _TYPE_MODEL

    if _TYPE_MODEL is None:
        if not INNOVATION_TYPE_MODEL_PATH.exists():
            raise FileNotFoundError(
                "Innovation-type model not found:\n"
                f"{INNOVATION_TYPE_MODEL_PATH}"
            )

        _TYPE_MODEL = joblib.load(
            INNOVATION_TYPE_MODEL_PATH
        )

    return _TYPE_MODEL


def _to_python_value(value: Any):
    """
    Convert NumPy scalar values to normal Python values.
    """
    if hasattr(value, "item"):
        return value.item()

    return value


def predict_innovation(text: str) -> dict:
    """
    Two-stage innovation prediction.

    Stage 1:
        innovation_required = True / False

    Stage 2:
        innovation_type is predicted only when
        innovation_required is True.

    Conservative policy:
        Required model confidence < 0.70
            -> human review

        Type model confidence < 0.70
        OR top1/top2 margin < 0.40
            -> human review
    """

    text = (text or "").strip()

    if not text:
        raise ValueError(
            "Innovation prediction requires non-empty text."
        )

    # ============================================================
    # STAGE 1 — INNOVATION REQUIRED
    # ============================================================

    required_model = _load_required_model()

    required_probabilities = (
        required_model.predict_proba([text])[0]
    )

    required_classes = [
        _to_python_value(value)
        for value in required_model.classes_
    ]

    required_prediction = (
        required_model.predict([text])[0]
    )

    required_prediction = bool(
        _to_python_value(required_prediction)
    )

    true_index = None

    for index, class_value in enumerate(
        required_classes
    ):
        if class_value is True:
            true_index = index
            break

    if true_index is None:
        raise RuntimeError(
            "Innovation-required model does not contain "
            "a TRUE class."
        )

    true_probability = float(
        required_probabilities[true_index]
    )

    required_confidence = float(
        max(required_probabilities)
    )

    required_decision = (
        "AUTO_CLASSIFY"
        if required_confidence
        >= REQUIRED_CONFIDENCE_THRESHOLD
        else "HUMAN_REVIEW"
    )

    # ============================================================
    # CASE 1 — INNOVATION NOT REQUIRED
    # ============================================================

    if not required_prediction:

        return {
            "innovation_required": False,
            "innovation_score": true_probability,

            "innovation_confidence": required_confidence,
            "innovation_decision": required_decision,
            "innovation_requires_human_review": (
                required_confidence
                < REQUIRED_CONFIDENCE_THRESHOLD
            ),

            "innovation_type": "NONE",
            "innovation_type_confidence": None,
            "innovation_type_second": None,
            "innovation_type_second_confidence": None,
            "innovation_type_margin": None,
            "innovation_type_decision": "NOT_APPLICABLE",
            "innovation_type_requires_human_review": False,
            "innovation_type_top_3": [],

            "innovation_reason": (
                "The innovation-required classifier predicts "
                "that the challenge can currently be handled "
                "without a specialized innovation pathway. "
                f"Model confidence: {required_confidence:.2f}."
            ),
        }

    # ============================================================
    # CASE 2 — INNOVATION REQUIRED
    # ============================================================

    type_model = _load_type_model()

    type_probabilities = (
        type_model.predict_proba([text])[0]
    )

    type_classes = [
        str(_to_python_value(value))
        for value in type_model.classes_
    ]

    type_indices = sorted(
        range(len(type_probabilities)),
        key=lambda index: type_probabilities[index],
        reverse=True,
    )

    top1_index = type_indices[0]
    top2_index = type_indices[1]

    top1_type = type_classes[top1_index]
    top2_type = type_classes[top2_index]

    top1_confidence = float(
        type_probabilities[top1_index]
    )

    top2_confidence = float(
        type_probabilities[top2_index]
    )

    type_margin = (
        top1_confidence
        - top2_confidence
    )

    top3 = []

    for rank, index in enumerate(
        type_indices[:3],
        start=1,
    ):
        top3.append(
            {
                "rank": rank,
                "innovation_type": type_classes[index],
                "confidence": float(
                    type_probabilities[index]
                ),
            }
        )

    type_requires_human_review = (
        top1_confidence
        < TYPE_CONFIDENCE_THRESHOLD
        or
        type_margin
        < TYPE_MARGIN_THRESHOLD
    )

    type_decision = (
        "HUMAN_REVIEW"
        if type_requires_human_review
        else "AUTO_CLASSIFY"
    )

    innovation_requires_human_review = (
        required_confidence
        < REQUIRED_CONFIDENCE_THRESHOLD
        or type_requires_human_review
    )

    overall_decision = (
        "HUMAN_REVIEW"
        if innovation_requires_human_review
        else "AUTO_CLASSIFY"
    )

    innovation_reason = (
        "The innovation-required classifier predicts that "
        "a specialized innovation pathway may be appropriate. "
        f"Required-model confidence: {required_confidence:.2f}. "
        f"Innovation type: {top1_type}. "
        f"Type confidence: {top1_confidence:.2f}. "
        f"Top-1/top-2 margin: {type_margin:.2f}."
    )

    if innovation_requires_human_review:
        innovation_reason += (
            " Human review is required because one or more "
            "innovation predictions do not meet the configured "
            "confidence or margin thresholds."
        )

    return {
        "innovation_required": True,
        "innovation_score": true_probability,

        "innovation_confidence": required_confidence,
        "innovation_decision": overall_decision,
        "innovation_requires_human_review": (
            innovation_requires_human_review
        ),

        "innovation_type": top1_type,
        "innovation_type_confidence": top1_confidence,

        "innovation_type_second": top2_type,
        "innovation_type_second_confidence": (
            top2_confidence
        ),

        "innovation_type_margin": type_margin,

        "innovation_type_decision": type_decision,

        "innovation_type_requires_human_review": (
            type_requires_human_review
        ),

        "innovation_type_top_3": top3,

        "innovation_reason": innovation_reason,
    }