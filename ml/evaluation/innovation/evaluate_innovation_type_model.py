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
    / "innovation_type_tfidf_logreg.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "innovation"
)


def main() -> None:
    print("=" * 80)
    print("INNOVATION TYPE MODEL EVALUATION")
    print("=" * 80)

    test_df = pd.read_csv(
        DATA_DIR / "test.csv"
    )

    # Only innovation-required cases.
    test_df = test_df[
        test_df["innovation_required"] == True
    ].copy()

    model = joblib.load(MODEL_PATH)

    X_test = test_df["text"].fillna("")
    y_test = test_df["innovation_type"]

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    classes = list(model.classes_)

    confidence = probabilities.max(axis=1)

    top_indices = probabilities.argsort(
        axis=1
    )[:, ::-1]

    top1_indices = top_indices[:, 0]
    top2_indices = top_indices[:, 1]

    top1_probability = probabilities[
        range(len(probabilities)),
        top1_indices,
    ]

    top2_probability = probabilities[
        range(len(probabilities)),
        top2_indices,
    ]

    margin = (
        top1_probability
        - top2_probability
    )

    top1_category = [
        classes[index]
        for index in top1_indices
    ]

    top2_category = [
        classes[index]
        for index in top2_indices
    ]

    correct = (
        predictions == y_test.to_numpy()
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
    )

    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=classes,
        )
    )

    results = test_df.copy()

    results["predicted_type"] = predictions
    results["prediction_confidence"] = confidence
    results["top1_category"] = top1_category
    results["top1_confidence"] = top1_probability
    results["top2_category"] = top2_category
    results["top2_confidence"] = top2_probability
    results["type_margin"] = margin
    results["correct"] = correct

    # ---------------------------------------------------------
    # Confidence analysis
    # ---------------------------------------------------------

    confidence_bins = [
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

    confidence_labels = [
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
        bins=confidence_bins,
        labels=confidence_labels,
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
    # Margin analysis
    # ---------------------------------------------------------

    margin_bins = [
        0.0,
        0.05,
        0.10,
        0.20,
        0.30,
        0.40,
        1.01,
    ]

    margin_labels = [
        "0.00-0.05",
        "0.05-0.10",
        "0.10-0.20",
        "0.20-0.30",
        "0.30-0.40",
        "0.40+",
    ]

    results["margin_band"] = pd.cut(
        results["type_margin"],
        bins=margin_bins,
        labels=margin_labels,
        include_lowest=True,
        right=False,
    )

    margin_analysis = (
        results
        .groupby(
            "margin_band",
            observed=False,
        )
        .agg(
            samples=("correct", "size"),
            correct=("correct", "sum"),
        )
    )

    margin_analysis["accuracy"] = (
        margin_analysis["correct"]
        / margin_analysis["samples"]
    )

    # ---------------------------------------------------------
    # Threshold analysis
    # ---------------------------------------------------------

    threshold_rows = []

    for threshold in [
        0.40,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
    ]:
        accepted = (
            results["prediction_confidence"]
            >= threshold
        )

        accepted_df = results[accepted]

        if accepted_df.empty:
            continue

        threshold_accuracy = (
            accepted_df["correct"].mean()
        )

        threshold_f1 = f1_score(
            accepted_df["innovation_type"],
            accepted_df["predicted_type"],
            average="macro",
        )

        threshold_rows.append(
            {
                "confidence_threshold": threshold,
                "auto_classified": len(accepted_df),
                "human_review": len(results)
                - len(accepted_df),
                "coverage": (
                    len(accepted_df)
                    / len(results)
                ),
                "auto_accuracy": threshold_accuracy,
                "auto_macro_f1": threshold_f1,
            }
        )

    threshold_df = pd.DataFrame(
        threshold_rows
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_path = (
        OUTPUT_DIR
        / "innovation_type_predictions.csv"
    )

    confidence_path = (
        OUTPUT_DIR
        / "innovation_type_confidence_analysis.csv"
    )

    margin_path = (
        OUTPUT_DIR
        / "innovation_type_margin_analysis.csv"
    )

    threshold_path = (
        OUTPUT_DIR
        / "innovation_type_threshold_analysis.csv"
    )

    misclassified_path = (
        OUTPUT_DIR
        / "innovation_type_misclassified.csv"
    )

    summary_path = (
        OUTPUT_DIR
        / "innovation_type_error_analysis_summary.json"
    )

    results.to_csv(
        results_path,
        index=False,
    )

    confidence_analysis.to_csv(
        confidence_path,
    )

    margin_analysis.to_csv(
        margin_path,
    )

    threshold_df.to_csv(
        threshold_path,
        index=False,
    )

    results[
        ~results["correct"]
    ].sort_values(
        "prediction_confidence",
        ascending=False,
    ).to_csv(
        misclassified_path,
        index=False,
    )

    summary = {
        "model_version": "innovation-type-tfidf-logreg-v1",
        "test_size": len(results),
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "mean_confidence": float(
            confidence.mean()
        ),
        "median_confidence": float(
            pd.Series(confidence).median()
        ),
        "mean_margin": float(
            margin.mean()
        ),
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

    print("\nConfidence Analysis:")
    print(
        confidence_analysis.to_string()
    )

    print("\nMargin Analysis:")
    print(
        margin_analysis.to_string()
    )

    print("\nThreshold Analysis:")
    print(
        threshold_df.to_string(index=False)
    )

    print("\nSaved:")
    print(results_path)
    print(confidence_path)
    print(margin_path)
    print(threshold_path)
    print(misclassified_path)
    print(summary_path)

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()