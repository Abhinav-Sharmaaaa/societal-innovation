from __future__ import annotations

import csv
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_ROOT = PROJECT_ROOT / "ml" / "data"

MASTER_FILE = (
    DATA_ROOT
    / "master"
    / "societal_challenges_master_v2.csv"
)

SPLITS_DIR = DATA_ROOT / "splits"
HOLDOUT_DIR = DATA_ROOT / "holdout"

OUTPUT_DIR = (
    DATA_ROOT
    / "training_views"
    / "category_classification"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "record_id",
    "challenge_id",
    "primary_category",
    "description",
    "problem_context",
    "citizen_statement",
    "state",
    "district",
    "language",
}


# ============================================================
# HELPERS
# ============================================================

def clean(value: str | None) -> str:
    """
    Normalize a CSV field.
    """
    if value is None:
        return ""

    return value.strip()


def build_text(row: dict[str, str]) -> str:
    """
    Build the model input text.

    Deliberately excludes the title to avoid relying on
    repeated/generic titles observed during dataset auditing.
    """

    parts = [
        f"Description: {clean(row.get('description'))}",
        f"Context: {clean(row.get('problem_context'))}",
        f"Citizen statement: {clean(row.get('citizen_statement'))}",
        f"State: {clean(row.get('state'))}",
        f"District: {clean(row.get('district'))}",
        f"Language: {clean(row.get('language'))}",
    ]

    valid_parts = [
        part
        for part in parts
        if part.split(":", 1)[-1].strip()
    ]

    return "\n".join(valid_parts)


# ============================================================
# PROCESS ONE SPLIT
# ============================================================

def process_split(
    input_path: Path,
    output_filename: str,
) -> None:

    output_path = OUTPUT_DIR / output_filename

    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing input split:\n{input_path}"
        )

    rows_read = 0
    rows_written = 0
    rows_skipped = 0

    with input_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as source:

        reader = csv.DictReader(source)

        fieldnames = set(reader.fieldnames or [])

        missing = REQUIRED_COLUMNS - fieldnames

        if missing:
            raise RuntimeError(
                f"{input_path.name} is missing required columns:\n"
                f"{sorted(missing)}"
            )

        with output_path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as target:

            output_fieldnames = [
                "record_id",
                "challenge_id",
                "text",
                "primary_category",
            ]

            writer = csv.DictWriter(
                target,
                fieldnames=output_fieldnames,
            )

            writer.writeheader()

            for row in reader:

                rows_read += 1

                record_id = clean(
                    row.get("record_id")
                )

                challenge_id = clean(
                    row.get("challenge_id")
                )

                category = clean(
                    row.get("primary_category")
                )

                text = build_text(row)

                if not record_id or not challenge_id:
                    rows_skipped += 1
                    continue

                if not category or not text:
                    rows_skipped += 1
                    continue

                writer.writerow(
                    {
                        "record_id": record_id,
                        "challenge_id": challenge_id,
                        "text": text,
                        "primary_category": category,
                    }
                )

                rows_written += 1

    print(
        f"{output_filename}: "
        f"{rows_written:,} rows "
        f"(read={rows_read:,}, skipped={rows_skipped:,})"
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print("CATEGORY CLASSIFICATION DATA PREPARATION")
    print("=" * 80)

    print("\nProject root:")
    print(PROJECT_ROOT)

    print("\nMaster:")
    print(MASTER_FILE)

    print("\nSplits directory:")
    print(SPLITS_DIR)

    print("\nHoldout directory:")
    print(HOLDOUT_DIR)

    print("\nOutput:")
    print(OUTPUT_DIR)

    # --------------------------------------------------------
    # Verify master
    # --------------------------------------------------------

    if not MASTER_FILE.exists():
        raise FileNotFoundError(
            f"Master dataset not found:\n{MASTER_FILE}"
        )

    # --------------------------------------------------------
    # Verify directories
    # --------------------------------------------------------

    if not SPLITS_DIR.exists():
        raise FileNotFoundError(
            f"Splits directory not found:\n{SPLITS_DIR}"
        )

    if not HOLDOUT_DIR.exists():
        raise FileNotFoundError(
            f"Holdout directory not found:\n{HOLDOUT_DIR}"
        )

    # --------------------------------------------------------
    # Standard train/validation/test splits
    # --------------------------------------------------------

    process_split(
        SPLITS_DIR / "train_v2.csv",
        "train.csv",
    )

    process_split(
        SPLITS_DIR / "validation_v2.csv",
        "validation.csv",
    )

    process_split(
        SPLITS_DIR / "test_v2.csv",
        "test.csv",
    )

    # --------------------------------------------------------
    # Geographic holdout
    # --------------------------------------------------------

    process_split(
        HOLDOUT_DIR / "geographic_holdout_test_v2.csv",
        "geographic_holdout_test.csv",
    )

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("CATEGORY DATASET PREPARATION COMPLETE")
    print("=" * 80)

    print("\nCreated files:")

    print(
        OUTPUT_DIR / "train.csv"
    )

    print(
        OUTPUT_DIR / "validation.csv"
    )

    print(
        OUTPUT_DIR / "test.csv"
    )

    print(
        OUTPUT_DIR / "geographic_holdout_test.csv"
    )


if __name__ == "__main__":
    main()