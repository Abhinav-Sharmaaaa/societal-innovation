from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "training_views"
    / "severity"
    / "train.csv"
)


def main() -> None:
    print("=" * 80)
    print("SEVERITY LABEL AUDIT")
    print("=" * 80)

    df = pd.read_csv(DATA_PATH)

    print(f"\nTotal rows: {len(df)}")

    print("\nSeverity distribution:")
    print(
        df["severity"]
        .value_counts()
        .sort_index()
    )

    print("\nAffected population statistics by severity:")
    print(
        df.groupby("severity")["affected_population"]
        .agg(
            [
                "count",
                "min",
                "mean",
                "median",
                "max",
            ]
        )
        .sort_index()
    )

    print("\nScope distribution by severity:")

    scope_table = pd.crosstab(
        df["severity"],
        df["scope"],
        normalize="index",
    ) * 100

    print(
        scope_table.round(2)
    )

    print("\nSeverity by population bands:")

    population_bins = [
        -1,
        10,
        50,
        100,
        500,
        1000,
        5000,
        10000,
        float("inf"),
    ]

    population_labels = [
        "0-10",
        "11-50",
        "51-100",
        "101-500",
        "501-1000",
        "1001-5000",
        "5001-10000",
        "10000+",
    ]

    df["population_band"] = pd.cut(
        df["affected_population"],
        bins=population_bins,
        labels=population_labels,
    )

    band_table = pd.crosstab(
        df["population_band"],
        df["severity"],
        normalize="index",
    ) * 100

    print(
        band_table.round(2)
    )

    print("\nMost common population values:")
    print(
        df["affected_population"]
        .value_counts()
        .head(20)
    )

    print("\nSeverity + scope combinations:")

    combination_table = (
        df.groupby(
            ["scope", "severity"]
        )
        .size()
        .unstack(fill_value=0)
    )

    print(combination_table)

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()