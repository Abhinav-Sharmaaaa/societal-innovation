from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "severity"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "severity"
)

EVALUATION_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "severity"
)


def main() -> None:
    print("=" * 80)
    print("SEVERITY TEXT-ONLY BASELINE")
    print("=" * 80)

    train_df = pd.read_csv(DATA_DIR / "train.csv")
    validation_df = pd.read_csv(DATA_DIR / "validation.csv")
    test_df = pd.read_csv(DATA_DIR / "test.csv")

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    solver="lbfgs",
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    X_train = train_df["text"].fillna("")
    y_train = train_df["severity"]

    X_validation = validation_df["text"].fillna("")
    y_validation = validation_df["severity"]

    X_test = test_df["text"].fillna("")
    y_test = test_df["severity"]

    print("\nTraining...")
    model.fit(X_train, y_train)

    validation_pred = model.predict(X_validation)
    test_pred = model.predict(X_test)

    validation_accuracy = accuracy_score(
        y_validation,
        validation_pred,
    )

    validation_f1 = f1_score(
        y_validation,
        validation_pred,
        average="macro",
    )

    test_accuracy = accuracy_score(
        y_test,
        test_pred,
    )

    test_f1 = f1_score(
        y_test,
        test_pred,
        average="macro",
    )

    print("\n" + "-" * 80)
    print("RESULTS")
    print("-" * 80)

    print(f"Validation Accuracy: {validation_accuracy:.4f}")
    print(f"Validation Macro F1: {validation_f1:.4f}")

    print(f"Test Accuracy:       {test_accuracy:.4f}")
    print(f"Test Macro F1:       {test_f1:.4f}")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    model_path = (
        MODEL_DIR
        / "severity_text_only_tfidf_logreg.joblib"
    )

    metrics_path = (
        EVALUATION_DIR
        / "severity_text_only_metrics.json"
    )

    joblib.dump(model, model_path)

    metrics = {
        "model_version": "severity-text-only-tfidf-logreg-v1",
        "model_type": "TF-IDF + Logistic Regression",
        "validation_accuracy": validation_accuracy,
        "validation_macro_f1": validation_f1,
        "test_accuracy": test_accuracy,
        "test_macro_f1": test_f1,
    }

    with metrics_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(metrics, f, indent=2)

    print("\nSaved:")
    print(model_path)
    print(metrics_path)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()