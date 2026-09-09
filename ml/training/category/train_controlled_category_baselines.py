from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_ROOT = PROJECT_ROOT / "ml" / "data"

SPLITS_DIR = DATA_ROOT / "splits"
HOLDOUT_DIR = DATA_ROOT / "holdout"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "category"
    / "controlled_baselines"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "category"
    / "controlled_baselines"
)

TRAIN_FILE = SPLITS_DIR / "train_v2.csv"
VALIDATION_FILE = SPLITS_DIR / "validation_v2.csv"
TEST_FILE = SPLITS_DIR / "test_v2.csv"
HOLDOUT_FILE = HOLDOUT_DIR / "geographic_holdout_test_v2.csv"

METRICS_FILE = OUTPUT_DIR / "controlled_baseline_metrics.json"


# ============================================================
# CONFIG
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
    "language",
]


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def load_split(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset:\n{path}")

    df = pd.read_csv(path)

    required = set(TEXT_COLUMNS + [TARGET] + METADATA_COLUMNS)
    missing = required - set(df.columns)

    if missing:
        raise RuntimeError(
            f"{path.name} is missing required columns: {sorted(missing)}"
        )

    for column in required:
        df[column] = df[column].fillna("").astype(str).str.strip()

    df = df[df[TARGET] != ""].copy()

    return df


def build_text(df: pd.DataFrame, variant: str) -> pd.Series:
    """
    Variant A: challenge text only.
    Variant B: challenge text + state + district.
    Variant C: challenge text + state + district + language.

    Title is intentionally excluded from all variants because the
    dataset audit found substantial title overlap across splits.
    """

    base = (
        "Description: " + df["description"] +
        "\nContext: " + df["problem_context"] +
        "\nCitizen statement: " + df["citizen_statement"]
    )

    if variant == "A_text_only":
        return base

    if variant == "B_text_plus_location":
        return (
            base
            + "\nState: " + df["state"]
            + "\nDistrict: " + df["district"]
        )

    if variant == "C_current_baseline":
        return (
            base
            + "\nState: " + df["state"]
            + "\nDistrict: " + df["district"]
            + "\nLanguage: " + df["language"]
        )

    raise ValueError(f"Unknown variant: {variant}")


def make_model() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    sublinear_tf=True,
                    max_features=150_000,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    solver="lbfgs",
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate(
    model: Pipeline,
    df: pd.DataFrame,
    X: pd.Series,
    split_name: str,
) -> dict:
    y_true = df[TARGET]
    y_pred = model.predict(X)

    return {
        "samples": int(len(df)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="macro",
            )
        ),
        "weighted_f1": float(
            f1_score(
                y_true,
                y_pred,
                average="weighted",
            )
        ),
    }


def main() -> None:
    print("=" * 80)
    print("SOCIETAL INNOVATION PLATFORM")
    print("CONTROLLED CATEGORY CLASSIFICATION BASELINES")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("\nLoading datasets...")

    train_df = load_split(TRAIN_FILE)
    validation_df = load_split(VALIDATION_FILE)
    test_df = load_split(TEST_FILE)
    holdout_df = load_split(HOLDOUT_FILE)

    print(f"Train      : {len(train_df):,}")
    print(f"Validation : {len(validation_df):,}")
    print(f"Test       : {len(test_df):,}")
    print(f"Holdout    : {len(holdout_df):,}")

    variants = {
        "A_text_only": "Challenge text only",
        "B_text_plus_location": "Challenge text + state + district",
        "C_current_baseline": "Challenge text + state + district + language",
    }

    all_metrics = {}

    for variant_name, description in variants.items():
        print("\n" + "=" * 80)
        print(f"TRAINING {variant_name}")
        print(description)
        print("=" * 80)

        X_train = build_text(train_df, variant_name)
        X_validation = build_text(validation_df, variant_name)
        X_test = build_text(test_df, variant_name)
        X_holdout = build_text(holdout_df, variant_name)

        model = make_model()

        print("\nFitting model...")
        model.fit(
            X_train,
            train_df[TARGET],
        )

        validation_metrics = evaluate(
            model,
            validation_df,
            X_validation,
            "validation",
        )

        test_metrics = evaluate(
            model,
            test_df,
            X_test,
            "test",
        )

        holdout_metrics = evaluate(
            model,
            holdout_df,
            X_holdout,
            "geographic_holdout",
        )

        all_metrics[variant_name] = {
            "description": description,
            "validation": validation_metrics,
            "test": test_metrics,
            "geographic_holdout": holdout_metrics,
        }

        print(
            f"\nValidation  : "
            f"{validation_metrics['accuracy']:.4f} accuracy | "
            f"{validation_metrics['macro_f1']:.4f} macro-F1"
        )

        print(
            f"Test        : "
            f"{test_metrics['accuracy']:.4f} accuracy | "
            f"{test_metrics['macro_f1']:.4f} macro-F1"
        )

        print(
            f"Geo holdout : "
            f"{holdout_metrics['accuracy']:.4f} accuracy | "
            f"{holdout_metrics['macro_f1']:.4f} macro-F1"
        )

        model_path = MODEL_DIR / f"{variant_name}.joblib"

        joblib.dump(
            model,
            model_path,
        )

        print(f"\nModel saved: {model_path}")

    # ========================================================
    # COMPARISON
    # ========================================================

    print("\n" + "=" * 80)
    print("CONTROLLED BASELINE COMPARISON")
    print("=" * 80)

    print(
        f"\n{'Variant':28s}"
        f"{'Val Acc':>12s}"
        f"{'Test Acc':>12s}"
        f"{'Holdout Acc':>14s}"
        f"{'Holdout F1':>14s}"
    )

    print("-" * 82)

    for variant_name, metrics in all_metrics.items():
        print(
            f"{variant_name:28s}"
            f"{metrics['validation']['accuracy']:>12.4f}"
            f"{metrics['test']['accuracy']:>12.4f}"
            f"{metrics['geographic_holdout']['accuracy']:>14.4f}"
            f"{metrics['geographic_holdout']['macro_f1']:>14.4f}"
        )

    with METRICS_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {
                "task": "primary_category_classification",
                "note": (
                    "Controlled experiment isolating the contribution "
                    "of text, location metadata, and language metadata."
                ),
                "variants": all_metrics,
            },
            f,
            indent=2,
        )

    print("\nMetrics saved:")
    print(METRICS_FILE)

    print("\n" + "=" * 80)
    print("CONTROLLED BASELINE EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
