from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "innovation"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "innovation"
    / "innovation_required_tfidf_logreg.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "innovation"
)


def main() -> None:
    print("=" * 80)
    print("INNOVATION MODEL EVALUATION")
    print("=" * 80)

    test_path = DATA_DIR / "test.csv"

    if not test_path.exists():
        raise FileNotFoundError(test_path)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)

    test_df = pd.read_csv(test_path)

    model = joblib.load(MODEL_PATH)

    X_test = test_df["text"].fillna("")
    y_test = test_df["innovation_required"].astype(bool)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    classes = model.classes_

    # Probability of TRUE
    true_index = list(classes).index(True)
    true_probability = probabilities[:, true_index]

    confidence = probabilities.max(axis=1)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
    )

    labels = [False, True]

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=labels,
            target_names=["FALSE", "TRUE"],
            zero_division=0,
        )
    )

    print("\nConfusion Matrix:")
    print(cm)

    # ---------------------------------------------------------
    # Attach predictions
    # ---------------------------------------------------------

    results = test_df.copy()

    results["predicted_innovation_required"] = predictions
    results["true_probability"] = true_probability
    results["prediction_confidence"] = confidence

    results["correct"] = (
        results["innovation_required"]
        == results["predicted_innovation_required"]
    )

    # ---------------------------------------------------------
    # Misclassified examples
    # ---------------------------------------------------------

    misclassified = results[
        ~results["correct"]
    ].copy()

    misclassified = misclassified.sort_values(
        "prediction_confidence",
        ascending=False,
    )

    # ---------------------------------------------------------
    # Confidence bands
    # ---------------------------------------------------------

    bins = [
        0.0,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
        0.95,
        0.98,
        1.01,
    ]

    labels_conf = [
        "0.00-0.50",
        "0.50-0.60",
        "0.60-0.70",
        "0.70-0.80",
        "0.80-0.90",
        "0.90-0.95",
        "0.95-0.98",
        "0.98-1.00",
    ]

    results["confidence_band"] = pd.cut(
        results["prediction_confidence"],
        bins=bins,
        labels=labels_conf,
        include_lowest=True,
        right=False,
    )

    confidence_analysis = (
        results
        .groupby(
            "confidence_band",
            observed=False,
        )
        .agg(
            samples=("correct", "size"),
            correct=("correct", "sum"),
        )
    )

    confidence_analysis["accuracy"] = (
        confidence_analysis["correct"]
        / confidence_analysis["samples"]
    )

    # ---------------------------------------------------------
    # Threshold analysis
    # ---------------------------------------------------------

    threshold_rows = []

    for threshold in [
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
    ]:
        accepted = (
            results["prediction_confidence"]
            >= threshold
        )

        accepted_df = results[accepted]

        if len(accepted_df) == 0:
            continue

        coverage = len(accepted_df) / len(results)

        accepted_accuracy = accepted_df["correct"].mean()

        accepted_f1 = f1_score(
            accepted_df["innovation_required"],
            accepted_df[
                "predicted_innovation_required"
            ],
            average="macro",
        )

        threshold_rows.append(
            {
                "threshold": threshold,
                "auto_classified": len(accepted_df),
                "human_review": len(results) - len(accepted_df),
                "coverage": coverage,
                "auto_accuracy": accepted_accuracy,
                "auto_macro_f1": accepted_f1,
            }
        )

    threshold_df = pd.DataFrame(threshold_rows)

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions_path = (
        OUTPUT_DIR
        / "test_predictions.csv"
    )

    misclassified_path = (
        OUTPUT_DIR
        / "misclassified_examples.csv"
    )

    confidence_path = (
        OUTPUT_DIR
        / "confidence_analysis.csv"
    )

    threshold_path = (
        OUTPUT_DIR
        / "threshold_analysis.csv"
    )

    summary_path = (
        OUTPUT_DIR
        / "error_analysis_summary.json"
    )

    results.to_csv(
        predictions_path,
        index=False,
    )

    misclassified.to_csv(
        misclassified_path,
        index=False,
    )

    confidence_analysis.to_csv(
        confidence_path,
    )

    threshold_df.to_csv(
        threshold_path,
        index=False,
    )

    summary = {
        "model_version": "innovation-required-tfidf-logreg-v1",
        "test_size": len(test_df),
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "misclassified_count": len(misclassified),
        "misclassification_rate": (
            len(misclassified) / len(test_df)
        ),
        "confusion_matrix": cm.tolist(),
    }

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    # ---------------------------------------------------------
    # Print confidence results
    # ---------------------------------------------------------

    print("\nConfidence Analysis:")
    print(
        confidence_analysis.to_string()
    )

    print("\nThreshold Analysis:")
    print(
        threshold_df.to_string(index=False)
    )

    print("\nSaved:")
    print(predictions_path)
    print(misclassified_path)
    print(confidence_path)
    print(threshold_path)
    print(summary_path)

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()