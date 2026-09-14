from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "instruction"
    / "urgency_training_v2.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "urgency"
    / "full.csv"
)


def main() -> None:
    print("=" * 80)
    print("URGENCY LABEL AUDIT")
    print("=" * 80)

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

            record = json.loads(line)

            temporal = record.get("temporal") or {}

            records.append(
                {
                    "text": str(
                        record.get("input", "")
                    ).strip(),
                    "urgency": str(
                        record.get("output", "")
                    ).strip().upper(),
                    "time_horizon": temporal.get(
                        "time_horizon"
                    ),
                    "recurrence": temporal.get(
                        "recurrence"
                    ),
                    "trend": temporal.get(
                        "trend"
                    ),
                }
            )

    df = pd.DataFrame(records)

    print(f"\nTotal rows: {len(df)}")

    print("\nUrgency distribution:")
    print(
        df["urgency"]
        .value_counts()
        .sort_index()
    )

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nTime horizon distribution:")
    print(
        df["time_horizon"]
        .value_counts(dropna=False)
    )

    print("\nRecurrence distribution:")
    print(
        df["recurrence"]
        .value_counts(dropna=False)
    )

    print("\nTrend distribution:")
    print(
        df["trend"]
        .value_counts(dropna=False)
    )

    print("\nUrgency by time horizon (%):")
    time_horizon_table = (
        pd.crosstab(
            df["urgency"],
            df["time_horizon"],
            normalize="index",
        )
        * 100
    )
    print(time_horizon_table.round(2))

    print("\nUrgency by recurrence (%):")
    recurrence_table = (
        pd.crosstab(
            df["urgency"],
            df["recurrence"],
            normalize="index",
        )
        * 100
    )
    print(recurrence_table.round(2))

    print("\nUrgency by trend (%):")
    trend_table = (
        pd.crosstab(
            df["urgency"],
            df["trend"],
            normalize="index",
        )
        * 100
    )
    print(trend_table.round(2))

    print("\nTime horizon + urgency:")
    print(
        pd.crosstab(
            df["time_horizon"],
            df["urgency"],
        )
    )

    print("\nRecurrence + urgency:")
    print(
        pd.crosstab(
            df["recurrence"],
            df["urgency"],
        )
    )

    print("\nTrend + urgency:")
    print(
        pd.crosstab(
            df["trend"],
            df["urgency"],
        )
    )

    print("\nThree-way temporal combinations:")
    combination = (
        df.groupby(
            [
                "time_horizon",
                "recurrence",
                "trend",
                "urgency",
            ]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False,
        )
    )

    print(combination.head(30).to_string(index=False))

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print("\nSaved:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
    