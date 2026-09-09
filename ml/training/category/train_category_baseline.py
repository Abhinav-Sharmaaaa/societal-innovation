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

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "category"
)

EVALUATION_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "category"
)

TRAIN_FILE = DATA_DIR / "train.csv"
VALIDATION_FILE = DATA_DIR / "validation.csv"
TEST_FILE = DATA_DIR / "test.csv"
HOLDOUT_FILE = DATA_DIR / "geographic_holdout_test.csv"

MODEL_FILE = (
    MODEL_DIR
    / "category_classifier_tfidf_logreg.joblib"
)

METRICS_FILE = (
    EVALUATION_DIR
    / "category_baseline_metrics.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

TEXT_COLUMN = "text"
TARGET_COLUMN = "primary_category"

TFIDF_CONFIG = {
    "ngram_range": (1, 2),
    "min_df": 2,
    "max_df": 0.98,
    "sublinear_tf": True,
    "max_features": 150_000,
}

LOGISTIC_CONFIG = {
    "max_iter": 1000,
    "class_weight": "balanced",
    "solver": "lbfgs",
    "random_state": 42,
}


# ============================================================
# DATA LOADING
# ============================================================

def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    df = pd.read_csv(path)

    required_columns = {
        TEXT_COLUMN,
        TARGET_COLUMN,
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"{path.name} is missing columns: "
            f"{sorted(missing)}"
        )

    df[TEXT_COLUMN] = (
        df[TEXT_COLUMN]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df[TARGET_COLUMN] = (
        df[TARGET_COLUMN]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df = df[
        (df[TEXT_COLUMN] != "")
        & (df[TARGET_COLUMN] != "")
    ].copy()

    return df


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    model: Pipeline,
    df: pd.DataFrame,
    dataset_name: str,
) -> dict:

    X = df[TEXT_COLUMN]
    y = df[TARGET_COLUMN]

    predictions = model.predict(X)

    accuracy = accuracy_score(
        y,
        predictions,
    )

    macro_f1 = f1_score(
        y,
        predictions,
        average="macro",
    )

    weighted_f1 = f1_score(
        y,
        predictions,
        average="weighted",
    )

    report = classification_report(
        y,
        predictions,
        output_dict=True,
        zero_division=0,
    )

    print("\n" + "=" * 80)
    print(f"{dataset_name.upper()} RESULTS")
    print("=" * 80)

    print(f"Samples       : {len(df):,}")
    print(f"Accuracy      : {accuracy:.4f}")
    print(f"Macro F1      : {macro_f1:.4f}")
    print(f"Weighted F1   : {weighted_f1:.4f}")

    print("\nClassification report:")
    print(
        classification_report(
            y,
            predictions,
            zero_division=0,
        )
    )

    return {
        "samples": int(len(df)),
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "classification_report": report,
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 80)
    print("SOCIETAL INNOVATION PLATFORM")
    print("CATEGORY CLASSIFICATION BASELINE")
    print("=" * 80)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nData directory:")
    print(DATA_DIR)

    print("\nLoading datasets...")

    train_df = load_dataset(TRAIN_FILE)
    validation_df = load_dataset(VALIDATION_FILE)
    test_df = load_dataset(TEST_FILE)
    holdout_df = load_dataset(HOLDOUT_FILE)

    print(f"\nTrain samples      : {len(train_df):,}")
    print(f"Validation samples : {len(validation_df):,}")
    print(f"Test samples       : {len(test_df):,}")
    print(f"Geo holdout        : {len(holdout_df):,}")

    # --------------------------------------------------------
    # Basic sanity checks
    # --------------------------------------------------------

    train_classes = set(
        train_df[TARGET_COLUMN].unique()
    )

    validation_classes = set(
        validation_df[TARGET_COLUMN].unique()
    )

    test_classes = set(
        test_df[TARGET_COLUMN].unique()
    )

    holdout_classes = set(
        holdout_df[TARGET_COLUMN].unique()
    )

    print("\nClasses:")
    for category in sorted(train_classes):
        print(
            f"  {category}: "
            f"{(train_df[TARGET_COLUMN] == category).sum():,}"
        )

    if validation_classes - train_classes:
        raise ValueError(
            "Validation contains classes not present in training:\n"
            f"{sorted(validation_classes - train_classes)}"
        )

    if test_classes - train_classes:
        raise ValueError(
            "Test contains classes not present in training:\n"
            f"{sorted(test_classes - train_classes)}"
        )

    if holdout_classes - train_classes:
        raise ValueError(
            "Geographic holdout contains classes not present in training:\n"
            f"{sorted(holdout_classes - train_classes)}"
        )

    # --------------------------------------------------------
    # Build model
    # --------------------------------------------------------

    print("\nBuilding TF-IDF + Logistic Regression model...")

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    **TFIDF_CONFIG,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    **LOGISTIC_CONFIG,
                ),
            ),
        ]
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    print("\nTraining model...")
    print("This may take some time with 50,400 records.")

    model.fit(
        train_df[TEXT_COLUMN],
        train_df[TARGET_COLUMN],
    )

    print("\nTraining complete.")

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    validation_metrics = evaluate_model(
        model,
        validation_df,
        "Validation",
    )

    test_metrics = evaluate_model(
        model,
        test_df,
        "Test",
    )

    holdout_metrics = evaluate_model(
        model,
        holdout_df,
        "Geographic Holdout",
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_FILE,
    )

    # --------------------------------------------------------
    # Save metrics
    # --------------------------------------------------------

    metrics = {
        "model": "TF-IDF + Logistic Regression",
        "task": "primary_category_classification",
        "tfidf_config": {
            "ngram_range": list(
                TFIDF_CONFIG["ngram_range"]
            ),
            "min_df": TFIDF_CONFIG["min_df"],
            "max_df": TFIDF_CONFIG["max_df"],
            "sublinear_tf": TFIDF_CONFIG["sublinear_tf"],
            "max_features": TFIDF_CONFIG["max_features"],
        },
        "logistic_regression_config": LOGISTIC_CONFIG,
        "classes": sorted(train_classes),
        "train_samples": int(len(train_df)),
        "validation": validation_metrics,
        "test": test_metrics,
        "geographic_holdout": holdout_metrics,
    }

    with METRICS_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            metrics,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("MODEL SAVED")
    print("=" * 80)

    print(MODEL_FILE)

    print("\nMetrics saved:")
    print(METRICS_FILE)

    print("\n" + "=" * 80)
    print("BASELINE TRAINING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()