from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
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


def load_split(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    df = pd.read_csv(path)

    required_columns = {
        "text",
        "severity",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing columns: {sorted(missing)}"
        )

    return df


def main() -> None:
    print("=" * 80)
    print("SEVERITY CLASSIFIER - TF-IDF + LOGISTIC REGRESSION")
    print("=" * 80)

    train_df = load_split("train.csv")
    validation_df = load_split("validation.csv")
    test_df = load_split("test.csv")

    print(f"Train rows:      {len(train_df)}")
    print(f"Validation rows: {len(validation_df)}")
    print(f"Test rows:       {len(test_df)}")

    X_train = train_df["text"].fillna("")
    y_train = train_df["severity"]

    X_validation = validation_df["text"].fillna("")
    y_validation = validation_df["severity"]

    X_test = test_df["text"].fillna("")
    y_test = test_df["severity"]

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

    print("\nTraining model...")
    model.fit(X_train, y_train)

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    validation_predictions = model.predict(X_validation)

    validation_accuracy = accuracy_score(
        y_validation,
        validation_predictions,
    )

    validation_macro_f1 = f1_score(
        y_validation,
        validation_predictions,
        average="macro",
    )

    validation_report = classification_report(
        y_validation,
        validation_predictions,
        output_dict=True,
        zero_division=0,
    )

    print("\n" + "-" * 80)
    print("VALIDATION")
    print("-" * 80)

    print(f"Accuracy:  {validation_accuracy:.4f}")
    print(f"Macro F1:  {validation_macro_f1:.4f}")

    # ---------------------------------------------------------
    # Test
    # ---------------------------------------------------------

    test_predictions = model.predict(X_test)

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    test_macro_f1 = f1_score(
        y_test,
        test_predictions,
        average="macro",
    )

    test_report = classification_report(
        y_test,
        test_predictions,
        output_dict=True,
        zero_division=0,
    )

    print("\n" + "-" * 80)
    print("TEST")
    print("-" * 80)

    print(f"Accuracy:  {test_accuracy:.4f}")
    print(f"Macro F1:  {test_macro_f1:.4f}")

    # ---------------------------------------------------------
    # Save model
    # ---------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = (
        MODEL_DIR
        / "severity_classifier_tfidf_logreg.joblib"
    )

    metrics_path = (
        EVALUATION_DIR
        / "severity_baseline_metrics.json"
    )

    joblib.dump(
        model,
        model_path,
    )

    metrics = {
        "model_version": "severity-tfidf-logreg-v1",
        "model_type": "TF-IDF + Logistic Regression",
        "classes": sorted(
            y_train.unique().tolist()
        ),
        "train_size": len(train_df),
        "validation_size": len(validation_df),
        "test_size": len(test_df),
        "validation_accuracy": validation_accuracy,
        "validation_macro_f1": validation_macro_f1,
        "test_accuracy": test_accuracy,
        "test_macro_f1": test_macro_f1,
        "validation_classification_report": validation_report,
        "test_classification_report": test_report,
    }

    with metrics_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=2,
        )

    print("\n" + "-" * 80)
    print("SAVED")
    print("-" * 80)

    print(f"Model:   {model_path}")
    print(f"Metrics: {metrics_path}")

    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()