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
    / "severity_training_v2.jsonl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "severity"
)


REQUIRED_LABELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


def build_text(record: dict) -> str:
    input_text = str(record.get("input", "")).strip()

    impact = record.get("impact") or {}

    affected_population = impact.get("affected_population")
    scope = impact.get("scope")

    parts = [
        input_text,
        f"Affected population: {affected_population}",
        f"Scope: {scope}",
    ]

    return "\n".join(
        part for part in parts if part and not part.endswith(": None")
    )


def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Source dataset not found:\n{SOURCE_FILE}"
        )

    records: list[dict] = []

    with SOURCE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            output = str(record.get("output", "")).strip().upper()

            if output not in REQUIRED_LABELS:
                raise ValueError(
                    f"Invalid severity label on line "
                    f"{line_number}: {output!r}"
                )

            text = build_text(record)

            if not text.strip():
                raise ValueError(
                    f"Empty training text on line {line_number}"
                )

            impact = record.get("impact") or {}

            records.append(
                {
                    "text": text,
                    "severity": output,
                    "affected_population": impact.get(
                        "affected_population"
                    ),
                    "scope": impact.get("scope"),
                }
            )

    df = pd.DataFrame(records)

    print("=" * 80)
    print("SEVERITY DATASET PREPARATION")
    print("=" * 80)

    print(f"Source: {SOURCE_FILE}")
    print(f"Total rows: {len(df)}")

    print("\nLabel distribution:")
    print(df["severity"].value_counts().sort_index())

    print("\nMissing values:")
    print(df.isna().sum())

    # Stratified train / validation / test split.
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["severity"],
    )

    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["severity"],
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

    print("\nSaved files:")
    print(train_path)
    print(validation_path)
    print(test_path)

    print("\nTrain distribution:")
    print(train_df["severity"].value_counts().sort_index())

    print("\nValidation distribution:")
    print(validation_df["severity"].value_counts().sort_index())

    print("\nTest distribution:")
    print(test_df["severity"].value_counts().sort_index())

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()