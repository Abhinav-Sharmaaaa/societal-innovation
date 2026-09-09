from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "category_classification"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "category"
    / "category_classifier_tfidf_logreg.joblib"
)

EVALUATION_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "category"
)

HOLDOUT_FILE = DATA_DIR / "geographic_holdout_test.csv"
TEST_FILE = DATA_DIR / "test.csv"

CONFUSION_MATRIX_FILE = EVALUATION_DIR / "confusion_matrix.png"
CLASSIFICATION_REPORT_FILE = EVALUATION_DIR / "classification_report.json"
MISCLASSIFIED_FILE = EVALUATION_DIR / "misclassified_examples.csv"
HOLDOUT_PREDICTIONS_FILE = EVALUATION_DIR / "holdout_predictions.csv"
ERROR_SUMMARY_FILE = EVALUATION_DIR / "error_analysis_summary.json"

TEXT_COLUMN = "text"
TARGET_COLUMN = "primary_category"


# ============================================================
# HELPERS
# ============================================================

def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found:\n{path}")

    df = pd.read_csv(path)

    required = {"record_id", "challenge_id", TEXT_COLUMN, TARGET_COLUMN}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{path.name} is missing required columns: {sorted(missing)}"
        )

    df[TEXT_COLUMN] = df[TEXT_COLUMN].fillna("").astype(str)
    df[TARGET_COLUMN] = df[TARGET_COLUMN].fillna("").astype(str).str.strip()
    return df


def top_confusions(y_true: pd.Series, y_pred, limit: int = 15):
    counts = Counter(
        (true, pred)
        for true, pred in zip(y_true, y_pred)
        if true != pred
    )
    return [
        {"actual": actual, "predicted": predicted, "count": count}
        for (actual, predicted), count in counts.most_common(limit)
    ]


def save_confusion_matrix(y_true: pd.Series, y_pred, labels: list[str]) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(14, 12))
    image = ax.imshow(cm, interpolation="nearest", aspect="auto")
    fig.colorbar(image, ax=ax)

    ax.set(
        xticks=range(len(labels)),
        yticks=range(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        ylabel="Actual category",
        xlabel="Predicted category",
        title="Category Classifier — Geographic Holdout Confusion Matrix",
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    threshold = cm.max() / 2.0 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center",
                color="white" if cm[i, j] > threshold else "black",
                fontsize=8,
            )

    fig.tight_layout()
    fig.savefig(CONFUSION_MATRIX_FILE, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print("=" * 80)
    print("SOCIETAL INNOVATION PLATFORM")
    print("CATEGORY CLASSIFIER ERROR ANALYSIS")
    print("=" * 80)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nModel:")
    print(MODEL_FILE)

    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Model not found:\n{MODEL_FILE}")

    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    print("\nLoading model...")
    model = joblib.load(MODEL_FILE)

    print("Loading geographic holdout...")
    holdout_df = load_dataset(HOLDOUT_FILE)

    print(f"Holdout samples: {len(holdout_df):,}")

    y_true = holdout_df[TARGET_COLUMN]
    predictions = model.predict(holdout_df[TEXT_COLUMN])

    labels = sorted(set(y_true) | set(predictions))

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    report_text = classification_report(
        y_true,
        predictions,
        labels=labels,
        zero_division=0,
    )

    report_dict = classification_report(
        y_true,
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    print("\n" + "=" * 80)
    print("GEOGRAPHIC HOLDOUT CLASSIFICATION REPORT")
    print("=" * 80)
    print(report_text)

    with CLASSIFICATION_REPORT_FILE.open("w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    # --------------------------------------------------------
    # Predictions file
    # --------------------------------------------------------

    prediction_df = holdout_df.copy()
    prediction_df["predicted_category"] = predictions
    prediction_df["correct"] = (
        prediction_df[TARGET_COLUMN] == prediction_df["predicted_category"]
    )

    try:
        probabilities = model.predict_proba(holdout_df[TEXT_COLUMN])
        prediction_df["prediction_confidence"] = probabilities.max(axis=1)
    except AttributeError:
        prediction_df["prediction_confidence"] = None

    prediction_df.to_csv(
        HOLDOUT_PREDICTIONS_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Misclassified examples
    # --------------------------------------------------------

    misclassified = prediction_df[
        ~prediction_df["correct"]
    ].copy()

    preferred_columns = [
        "record_id",
        "challenge_id",
        TARGET_COLUMN,
        "predicted_category",
        "prediction_confidence",
        TEXT_COLUMN,
    ]

    available_columns = [
        column for column in preferred_columns
        if column in misclassified.columns
    ]

    misclassified[available_columns].to_csv(
        MISCLASSIFIED_FILE,
        index=False,
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    save_confusion_matrix(
        y_true,
        predictions,
        labels,
    )

    # --------------------------------------------------------
    # Top confusions
    # --------------------------------------------------------

    confusion_pairs = top_confusions(
        y_true,
        predictions,
        limit=20,
    )

    print("=" * 80)
    print("TOP CATEGORY CONFUSIONS")
    print("=" * 80)

    if confusion_pairs:
        for item in confusion_pairs:
            print(
                f"{item['actual']} -> {item['predicted']}: "
                f"{item['count']} cases"
            )
    else:
        print("No misclassifications found.")

    # --------------------------------------------------------
    # Per-class error counts
    # --------------------------------------------------------

    true_counts = y_true.value_counts().to_dict()
    correct_counts = prediction_df.groupby(TARGET_COLUMN)["correct"].sum().to_dict()

    per_class_errors = {}
    for category in labels:
        total = int(true_counts.get(category, 0))
        correct = int(correct_counts.get(category, 0))
        errors = total - correct
        per_class_errors[category] = {
            "total": total,
            "correct": correct,
            "errors": errors,
            "error_rate": (errors / total) if total else 0.0,
        }

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    total = len(prediction_df)
    errors = len(misclassified)
    accuracy = (total - errors) / total if total else 0.0

    summary = {
        "dataset": "geographic_holdout_test",
        "samples": int(total),
        "correct": int(total - errors),
        "misclassified": int(errors),
        "accuracy": float(accuracy),
        "top_confusions": confusion_pairs,
        "per_class_errors": per_class_errors,
        "artifacts": {
            "confusion_matrix": str(CONFUSION_MATRIX_FILE),
            "classification_report": str(CLASSIFICATION_REPORT_FILE),
            "misclassified_examples": str(MISCLASSIFIED_FILE),
            "holdout_predictions": str(HOLDOUT_PREDICTIONS_FILE),
        },
    }

    with ERROR_SUMMARY_FILE.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print("ERROR ANALYSIS COMPLETE")
    print("=" * 80)

    print(f"\nTotal holdout samples : {total:,}")
    print(f"Correct predictions   : {total - errors:,}")
    print(f"Misclassified         : {errors:,}")
    print(f"Accuracy              : {accuracy:.4f}")

    print("\nCreated artifacts:")
    print(CONFUSION_MATRIX_FILE)
    print(CLASSIFICATION_REPORT_FILE)
    print(MISCLASSIFIED_FILE)
    print(HOLDOUT_PREDICTIONS_FILE)
    print(ERROR_SUMMARY_FILE)


if __name__ == "__main__":
    main()