from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_ROOT = PROJECT_ROOT / "ml" / "data"

HOLDOUT_FILE = (
    DATA_ROOT
    / "holdout"
    / "geographic_holdout_test_v2.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "category"
    / "controlled_baselines"
    / "B_text_plus_location.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "category"
    / "confidence_analysis"
)

SUMMARY_FILE = OUTPUT_DIR / "confidence_analysis_summary.json"
PREDICTIONS_FILE = OUTPUT_DIR / "holdout_confidence_predictions.csv"
THRESHOLD_FILE = OUTPUT_DIR / "threshold_analysis.csv"


# ============================================================
# CONFIGURATION
# ============================================================

TARGET = "primary_category"

TEXT_COLUMNS = [
    "description",
    "problem_context",
    "citizen_statement",
]

METADATA_COLUMNS = [
    "state",
    "district",
]

# Confidence thresholds to evaluate.
THRESHOLDS = [
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
    0.98,
]


# ============================================================
# HELPERS
# ============================================================

def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_holdout() -> pd.DataFrame:
    if not HOLDOUT_FILE.exists():
        raise FileNotFoundError(
            f"Holdout dataset not found:\n{HOLDOUT_FILE}"
        )

    df = pd.read_csv(HOLDOUT_FILE)

    required = set(TEXT_COLUMNS + METADATA_COLUMNS + [TARGET])

    missing = required - set(df.columns)

    if missing:
        raise RuntimeError(
            f"Holdout is missing required columns: {sorted(missing)}"
        )

    for column in required:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df = df[df[TARGET] != ""].copy()

    return df


def build_text(df: pd.DataFrame) -> pd.Series:
    """
    Must exactly match the winning B_text_plus_location
    controlled baseline:
      challenge text + state + district

    Title and language are intentionally excluded.
    """

    return (
        "Description: " + df["description"]
        + "\nContext: " + df["problem_context"]
        + "\nCitizen statement: " + df["citizen_statement"]
        + "\nState: " + df["state"]
        + "\nDistrict: " + df["district"]
    )


def get_probability_outputs(
    model,
    X: pd.Series,
):
    """
    Return predicted class, top-1 probability,
    top-2 probability, and top-1/top-2 margin.
    """

    probabilities = model.predict_proba(X)
    classes = np.asarray(model.classes_)

    top_indices = np.argsort(
        probabilities,
        axis=1,
    )[:, ::-1]

    top1_indices = top_indices[:, 0]
    top2_indices = top_indices[:, 1]

    top1_probability = probabilities[
        np.arange(len(probabilities)),
        top1_indices,
    ]

    top2_probability = probabilities[
        np.arange(len(probabilities)),
        top2_indices,
    ]

    margin = (
        top1_probability
        - top2_probability
    )

    predicted = classes[top1_indices]

    return (
        predicted,
        top1_probability,
        top2_probability,
        margin,
        probabilities,
        classes,
    )


def evaluate_threshold(
    y_true: np.ndarray,
    predictions: np.ndarray,
    confidence: np.ndarray,
    threshold: float,
) -> dict:

    accepted = confidence >= threshold

    accepted_count = int(accepted.sum())
    rejected_count = int((~accepted).sum())

    coverage = (
        accepted_count / len(y_true)
        if len(y_true)
        else 0.0
    )

    if accepted_count:
        accepted_accuracy = accuracy_score(
            y_true[accepted],
            predictions[accepted],
        )

        accepted_macro_f1 = f1_score(
            y_true[accepted],
            predictions[accepted],
            average="macro",
            zero_division=0,
        )
    else:
        accepted_accuracy = 0.0
        accepted_macro_f1 = 0.0

    return {
        "threshold": threshold,
        "accepted_samples": accepted_count,
        "human_review_samples": rejected_count,
        "coverage": coverage,
        "accepted_accuracy": float(accepted_accuracy),
        "accepted_macro_f1": float(accepted_macro_f1),
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("=" * 80)
    print("SOCIETAL INNOVATION PLATFORM")
    print("CATEGORY CONFIDENCE ANALYSIS")
    print("=" * 80)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nModel:")
    print(MODEL_FILE)

    print("\nHoldout:")
    print(HOLDOUT_FILE)

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Model not found:\n{MODEL_FILE}"
        )

    print("\nLoading model...")
    model = joblib.load(MODEL_FILE)

    print("Loading geographic holdout...")
    df = load_holdout()

    print(f"Holdout samples: {len(df):,}")

    X = build_text(df)
    y_true = df[TARGET].to_numpy()

    (
        predictions,
        top1_probability,
        top2_probability,
        margin,
        probabilities,
        classes,
    ) = get_probability_outputs(
        model,
        X,
    )

    # ========================================================
    # OVERALL METRICS
    # ========================================================

    overall_accuracy = accuracy_score(
        y_true,
        predictions,
    )

    overall_macro_f1 = f1_score(
        y_true,
        predictions,
        average="macro",
        zero_division=0,
    )

    correct = (
        y_true == predictions
    )

    print("\n" + "=" * 80)
    print("OVERALL HOLDOUT")
    print("=" * 80)

    print(f"Accuracy    : {overall_accuracy:.4f}")
    print(f"Macro F1    : {overall_macro_f1:.4f}")
    print(
        f"Mean confidence: "
        f"{top1_probability.mean():.4f}"
    )

    print(
        f"Median confidence: "
        f"{np.median(top1_probability):.4f}"
    )

    print(
        f"Mean top-1/top-2 margin: "
        f"{margin.mean():.4f}"
    )

    # ========================================================
    # CONFIDENCE BAND ANALYSIS
    # ========================================================

    confidence_bands = [
        (0.00, 0.50),
        (0.50, 0.60),
        (0.60, 0.70),
        (0.70, 0.80),
        (0.80, 0.90),
        (0.90, 0.95),
        (0.95, 0.98),
        (0.98, 1.01),
    ]

    band_results = []

    print("\n" + "=" * 80)
    print("CONFIDENCE BANDS")
    print("=" * 80)

    print(
        f"\n{'Band':15s}"
        f"{'Samples':>10s}"
        f"{'Accuracy':>12s}"
        f"{'Error':>10s}"
    )

    print("-" * 50)

    for lower, upper in confidence_bands:
        mask = (
            (top1_probability >= lower)
            & (top1_probability < upper)
        )

        count = int(mask.sum())

        if count:
            accuracy = float(
                correct[mask].mean()
            )
        else:
            accuracy = 0.0

        error_rate = 1.0 - accuracy

        label = (
            f"{lower:.2f}-{upper:.2f}"
            if upper <= 1.0
            else f"{lower:.2f}-1.00"
        )

        band_results.append(
            {
                "lower": lower,
                "upper": upper,
                "samples": count,
                "accuracy": accuracy,
                "error_rate": error_rate,
                "coverage": (
                    count / len(df)
                    if len(df)
                    else 0.0
                ),
            }
        )

        print(
            f"{label:15s}"
            f"{count:>10,}"
            f"{accuracy:>12.4f}"
            f"{error_rate:>10.4f}"
        )

    # ========================================================
    # THRESHOLD ANALYSIS
    # ========================================================

    threshold_results = []

    print("\n" + "=" * 80)
    print("CONFIDENCE THRESHOLD ANALYSIS")
    print("=" * 80)

    print(
        f"\n{'Threshold':>10s}"
        f"{'Auto':>10s}"
        f"{'Review':>10s}"
        f"{'Coverage':>12s}"
        f"{'Auto Acc':>12s}"
        f"{'Auto F1':>12s}"
    )

    print("-" * 70)

    for threshold in THRESHOLDS:
        result = evaluate_threshold(
            y_true,
            predictions,
            top1_probability,
            threshold,
        )

        threshold_results.append(result)

        print(
            f"{threshold:>10.2f}"
            f"{result['accepted_samples']:>10,}"
            f"{result['human_review_samples']:>10,}"
            f"{result['coverage']:>12.2%}"
            f"{result['accepted_accuracy']:>12.4f}"
            f"{result['accepted_macro_f1']:>12.4f}"
        )

    threshold_df = pd.DataFrame(
        threshold_results
    )

    threshold_df.to_csv(
        THRESHOLD_FILE,
        index=False,
    )

    # ========================================================
    # MARGIN ANALYSIS
    # ========================================================

    margin_bins = [
        (0.00, 0.05),
        (0.05, 0.10),
        (0.10, 0.20),
        (0.20, 0.30),
        (0.30, 0.40),
        (0.40, 1.01),
    ]

    margin_results = []

    print("\n" + "=" * 80)
    print("TOP-1 / TOP-2 MARGIN ANALYSIS")
    print("=" * 80)

    print(
        f"\n{'Margin Band':15s}"
        f"{'Samples':>10s}"
        f"{'Accuracy':>12s}"
        f"{'Error':>10s}"
    )

    print("-" * 50)

    for lower, upper in margin_bins:
        mask = (
            (margin >= lower)
            & (margin < upper)
        )

        count = int(mask.sum())

        if count:
            accuracy = float(
                correct[mask].mean()
            )
        else:
            accuracy = 0.0

        error_rate = 1.0 - accuracy

        margin_results.append(
            {
                "lower": lower,
                "upper": upper,
                "samples": count,
                "accuracy": accuracy,
                "error_rate": error_rate,
                "coverage": (
                    count / len(df)
                    if len(df)
                    else 0.0
                ),
            }
        )

        print(
            f"{lower:.2f}-{upper:.2f}{'':5s}"
            f"{count:>10,}"
            f"{accuracy:>12.4f}"
            f"{error_rate:>10.4f}"
        )

    # ========================================================
    # PREDICTION ARTIFACT
    # ========================================================

    # Sort all classes by probability in descending order.
    # top_indices[:, 0] = top-1 class
    # top_indices[:, 1] = top-2 class
    # top_indices[:, 2] = top-3 class
    top_indices = np.argsort(
        probabilities,
        axis=1,
    )[:, ::-1]

    top3_indices = top_indices[:, :3]

    prediction_df = pd.DataFrame(
        {
            "record_id": df.get(
                "record_id",
                pd.Series(
                    ["" for _ in range(len(df))]
                ),
            ).to_numpy(),
            "challenge_id": df.get(
                "challenge_id",
                pd.Series(
                    ["" for _ in range(len(df))]
                ),
            ).to_numpy(),
            "primary_category": y_true,
            "predicted_category": predictions,
            "correct": correct,
            "prediction_confidence": top1_probability,
            "second_best_confidence": top2_probability,
            "top1_top2_margin": margin,
            "top2_category": classes[
                top_indices[:, 1]
            ],
            "top3_category": classes[
                top_indices[:, 2]
            ],
            "state": df["state"].to_numpy(),
            "district": df["district"].to_numpy(),
            "language": (
                df["language"].to_numpy()
                if "language" in df.columns
                else np.array([""] * len(df))
            ),
            "description": df["description"].to_numpy(),
        }
    )

    prediction_df.to_csv(
        PREDICTIONS_FILE,
        index=False,
    )

    # ========================================================
    # RECOMMENDATION
    # ========================================================

    # Conservative candidate threshold:
    # choose the lowest threshold reaching >=99% accepted accuracy,
    # if such a threshold exists. Otherwise report the best
    # accepted accuracy without inventing a target.
    eligible = threshold_df[
        threshold_df["accepted_accuracy"] >= 0.99
    ]

    if not eligible.empty:
        recommended = eligible.sort_values(
            "threshold",
            ascending=True,
        ).iloc[0]
        recommendation = {
            "recommended_threshold": float(
                recommended["threshold"]
            ),
            "reason": (
                "Lowest evaluated confidence threshold "
                "whose automatically accepted samples reached "
                "at least 99% accuracy on the geographic holdout."
            ),
            "expected_auto_coverage": float(
                recommended["coverage"]
            ),
            "expected_human_review_rate": float(
                1.0 - recommended["coverage"]
            ),
            "accepted_accuracy": float(
                recommended["accepted_accuracy"]
            ),
            "accepted_macro_f1": float(
                recommended["accepted_macro_f1"]
            ),
        }
    else:
        recommendation = {
            "recommended_threshold": None,
            "reason": (
                "No evaluated threshold reached 99% accepted "
                "accuracy on the current geographic holdout. "
                "Do not claim a 99%-accuracy auto-routing threshold."
            ),
        }

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = {
        "model": str(MODEL_FILE),
        "dataset": str(HOLDOUT_FILE),
        "samples": int(len(df)),
        "overall": {
            "accuracy": float(overall_accuracy),
            "macro_f1": float(overall_macro_f1),
            "mean_confidence": float(top1_probability.mean()),
            "median_confidence": float(
                np.median(top1_probability)
            ),
            "mean_top1_top2_margin": float(
                margin.mean()
            ),
        },
        "confidence_bands": band_results,
        "thresholds": threshold_results,
        "margin_bands": margin_results,
        "recommendation": recommendation,
        "note": (
            "Confidence values are model probabilities from the "
            "logistic regression classifier. They are not automatically "
            "calibrated probabilities. Threshold results are empirical "
            "holdout measurements and should be validated on real-world "
            "human-reviewed cases before production use."
        ),
    }

    with SUMMARY_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            indent=2,
        )

    # ========================================================
    # FINAL
    # ========================================================

    print("\n" + "=" * 80)
    print("CONFIDENCE ANALYSIS COMPLETE")
    print("=" * 80)

    print("\nCreated artifacts:")
    print(PREDICTIONS_FILE)
    print(THRESHOLD_FILE)
    print(SUMMARY_FILE)

    print("\nRecommendation:")
    if recommendation["recommended_threshold"] is None:
        print(
            "No >=99% accepted-accuracy threshold was found."
        )
    else:
        print(
            f"Threshold: "
            f"{recommendation['recommended_threshold']:.2f}"
        )
        print(
            f"Auto coverage: "
            f"{recommendation['expected_auto_coverage']:.2%}"
        )
        print(
            f"Human review: "
            f"{recommendation['expected_human_review_rate']:.2%}"
        )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
