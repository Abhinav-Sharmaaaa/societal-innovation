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
    / "innovation"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "innovation"
)

EVALUATION_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "innovation"
)


def load_split(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    df = pd.read_csv(path)

    required = {
        "text",
        "innovation_required",
        "innovation_type",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} is missing columns: "
            f"{sorted(missing)}"
        )

    return df


def main() -> None:
    print("=" * 80)
    print("INNOVATION TYPE CLASSIFIER")
    print("ENGINEERING / PROCESS_INNOVATION / RESEARCH_REQUIRED")
    print("TF-IDF + LOGISTIC REGRESSION")
    print("=" * 80)

    train_df = load_split("train.csv")
    validation_df = load_split("validation.csv")
    test_df = load_split("test.csv")

    # Only TRUE innovation cases are relevant for type classification.
    train_df = train_df[
        train_df["innovation_required"] == True
    ].copy()

    validation_df = validation_df[
        validation_df["innovation_required"] == True
    ].copy()

    test_df = test_df[
        test_df["innovation_required"] == True
    ].copy()

    print(f"\nTrain rows:      {len(train_df)}")
    print(f"Validation rows: {len(validation_df)}")
    print(f"Test rows:       {len(test_df)}")

    print("\nTraining type distribution:")
    print(
        train_df["innovation_type"]
        .value_counts()
        .sort_index()
    )

    X_train = train_df["text"].fillna("")
    y_train = train_df["innovation_type"]

    X_validation = validation_df["text"].fillna("")
    y_validation = validation_df["innovation_type"]

    X_test = test_df["text"].fillna("")
    y_test = test_df["innovation_type"]

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

    validation_predictions = model.predict(
        X_validation
    )

    test_predictions = model.predict(X_test)

    validation_accuracy = accuracy_score(
        y_validation,
        validation_predictions,
    )

    validation_macro_f1 = f1_score(
        y_validation,
        validation_predictions,
        average="macro",
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    test_macro_f1 = f1_score(
        y_test,
        test_predictions,
        average="macro",
    )

    validation_report = classification_report(
        y_validation,
        validation_predictions,
        output_dict=True,
        zero_division=0,
    )

    test_report = classification_report(
        y_test,
        test_predictions,
        output_dict=True,
        zero_division=0,
    )

    print("\n" + "-" * 80)
    print("VALIDATION")
    print("-" * 80)

    print(f"Accuracy:  {validation_accuracy:.4f}")
    print(f"Macro F1:  {validation_macro_f1:.4f}")

    print("\n" + "-" * 80)
    print("TEST")
    print("-" * 80)

    print(f"Accuracy:  {test_accuracy:.4f}")
    print(f"Macro F1:  {test_macro_f1:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            test_predictions,
            zero_division=0,
        )
    )

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
        / "innovation_type_tfidf_logreg.joblib"
    )

    metrics_path = (
        EVALUATION_DIR
        / "innovation_type_metrics.json"
    )

    joblib.dump(
        model,
        model_path,
    )

    metrics = {
        "model_version": "innovation-type-tfidf-logreg-v1",
        "model_type": "TF-IDF + Logistic Regression",
        "train_size": len(train_df),
        "validation_size": len(validation_df),
        "test_size": len(test_df),
        "classes": sorted(
            y_train.unique().tolist()
        ),
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

    print("\nSaved:")
    print(model_path)
    print(metrics_path)

    print("\n" + "=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()