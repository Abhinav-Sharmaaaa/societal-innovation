from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "instruction"
    / "innovation_training_v2.jsonl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "innovation"
)


VALID_TYPES = {
    "NONE",
    "PROCESS_INNOVATION",
    "RESEARCH_REQUIRED",
    "ENGINEERING",
}


def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{SOURCE_FILE}"
        )

    records = []

    with SOURCE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            text = str(
                record.get("input", "")
            ).strip()

            output = record.get("output") or {}

            innovation_required = output.get(
                "innovation_required"
            )

            innovation_type = str(
                output.get(
                    "innovation_type",
                    "",
                )
            ).strip().upper()

            if not text:
                raise ValueError(
                    f"Empty input on line {line_number}"
                )

            if not isinstance(
                innovation_required,
                bool,
            ):
                raise ValueError(
                    f"Invalid innovation_required on "
                    f"line {line_number}: "
                    f"{innovation_required!r}"
                )

            if innovation_type not in VALID_TYPES:
                raise ValueError(
                    f"Invalid innovation_type on "
                    f"line {line_number}: "
                    f"{innovation_type!r}"
                )

            records.append(
                {
                    "text": text,
                    "innovation_required": innovation_required,
                    "innovation_type": innovation_type,
                }
            )

    df = pd.DataFrame(records)

    print("=" * 80)
    print("INNOVATION DATASET PREPARATION")
    print("=" * 80)

    print(f"\nTotal rows: {len(df)}")

    print("\nInnovation required distribution:")
    print(
        df["innovation_required"]
        .value_counts()
        .sort_index()
    )

    print("\nInnovation type distribution:")
    print(
        df["innovation_type"]
        .value_counts()
        .sort_index()
    )

    print("\nCross-tabulation:")
    print(
        pd.crosstab(
            df["innovation_required"],
            df["innovation_type"],
        )
    )

    # Stratify using the four innovation types.
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["innovation_type"],
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["innovation_type"],
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_path = OUTPUT_DIR / "train.csv"
    validation_path = OUTPUT_DIR / "validation.csv"
    test_path = OUTPUT_DIR / "test.csv"

    train_df.to_csv(
        train_path,
        index=False,
        encoding="utf-8",
    )

    validation_df.to_csv(
        validation_path,
        index=False,
        encoding="utf-8",
    )

    test_df.to_csv(
        test_path,
        index=False,
        encoding="utf-8",
    )

    print("\nSplit sizes:")
    print(f"Train:      {len(train_df)}")
    print(f"Validation: {len(validation_df)}")
    print(f"Test:       {len(test_df)}")

    print("\nTrain innovation type distribution:")
    print(
        train_df["innovation_type"]
        .value_counts()
        .sort_index()
    )

    print("\nValidation innovation type distribution:")
    print(
        validation_df["innovation_type"]
        .value_counts()
        .sort_index()
    )

    print("\nTest innovation type distribution:")
    print(
        test_df["innovation_type"]
        .value_counts()
        .sort_index()
    )

    print("\nSaved:")
    print(train_path)
    print(validation_path)
    print(test_path)

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()