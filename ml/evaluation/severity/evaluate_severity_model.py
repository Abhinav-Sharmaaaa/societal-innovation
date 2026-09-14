from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
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
    / "severity"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "severity"
    / "severity_classifier_tfidf_logreg.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "severity"
)


def main() -> None:
    print("=" * 80)
    print("SEVERITY MODEL EVALUATION")
    print("=" * 80)

    test_path = DATA_DIR / "test.csv"

    if not test_path.exists():
        raise FileNotFoundError(test_path)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(MODEL_PATH)

    test_df = pd.read_csv(test_path)

    model = joblib.load(MODEL_PATH)

    X_test = test_df["text"].fillna("")
    y_test = test_df["severity"]

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)
    classes = model.classes_

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

    labels = sorted(y_test.unique())

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    report = classification_report(
        y_test,
        predictions,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=labels,
            zero_division=0,
        )
    )

    print("\nConfusion Matrix:")
    print("Labels:", labels)
    print(cm)

    # ---------------------------------------------------------
    # Save confusion matrix image
    # ---------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Severity Confusion Matrix")
    plt.colorbar()

    plt.xticks(
        range(len(labels)),
        labels,
        rotation=45,
        ha="right",
    )

    plt.yticks(
        range(len(labels)),
        labels,
    )

    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for i in range(len(labels)):
        for j in range(len(labels)):
            plt.text(
                j,
                i,
                cm[i, j],
                ha="center",
                va="center",
            )

    plt.tight_layout()

    confusion_path = (
        OUTPUT_DIR
        / "confusion_matrix.png"
    )

    plt.savefig(
        confusion_path,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    # ---------------------------------------------------------
    # Save misclassified examples
    # ---------------------------------------------------------

    result_df = test_df.copy()

    result_df["predicted_severity"] = predictions
    result_df["prediction_confidence"] = confidence

    misclassified = result_df[
        result_df["severity"] != result_df["predicted_severity"]
    ].copy()

    misclassified = misclassified.sort_values(
        "prediction_confidence",
        ascending=False,
    )

    misclassified_path = (
        OUTPUT_DIR
        / "misclassified_examples.csv"
    )

    misclassified.to_csv(
        misclassified_path,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # Save predictions
    # ---------------------------------------------------------

    predictions_path = (
        OUTPUT_DIR
        / "test_predictions.csv"
    )

    result_df.to_csv(
        predictions_path,
        index=False,
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # Save summary
    # ---------------------------------------------------------

    summary = {
        "model": "severity-tfidf-logreg-v1",
        "test_size": len(test_df),
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "misclassified_count": len(misclassified),
        "misclassification_rate": (
            len(misclassified) / len(test_df)
        ),
        "labels": labels,
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }

    summary_path = (
        OUTPUT_DIR
        / "error_analysis_summary.json"
    )

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    print("\nSaved:")
    print(confusion_path)
    print(misclassified_path)
    print(predictions_path)
    print(summary_path)

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()