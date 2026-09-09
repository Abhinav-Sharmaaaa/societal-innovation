from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_ROOT = PROJECT_ROOT / "ml" / "data"

MASTER_FILE = (
    DATA_ROOT
    / "master"
    / "societal_challenges_master_v2.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "ml"
    / "evaluation"
    / "category"
    / "label_audit"
)

REVIEW_FILE = OUTPUT_DIR / "suspicious_category_examples.csv"
SUMMARY_FILE = OUTPUT_DIR / "category_label_audit_summary.json"


# ============================================================
# CATEGORY-SPECIFIC SIGNALS
#
# These are REVIEW HEURISTICS only.
# They do not change labels automatically.
# ============================================================

CATEGORY_SIGNALS = {
    "AGRICULTURE": [
        "agriculture", "farmer", "farmers", "crop", "crops",
        "irrigation", "farming", "livestock", "fertilizer",
        "soil", "harvest", "pesticide", "horticulture",
    ],
    "DIGITAL_SERVICES": [
        "digital service", "online service", "portal", "website",
        "app", "application", "internet", "connectivity",
        "e-governance", "digital", "online", "broadband",
    ],
    "DISASTER_MANAGEMENT": [
        "disaster", "flood", "floods", "earthquake", "landslide",
        "rockfall", "cyclone", "drought", "wildfire", "forest fire",
        "emergency response", "disaster response", "evacuation",
        "relief", "rescue", "hazard",
    ],
    "EDUCATION": [
        "education", "school", "schools", "student", "students",
        "teacher", "teachers", "learning", "classroom", "college",
        "university", "vocational training", "literacy",
        "curriculum", "scholarship",
    ],
    "EMPLOYMENT": [
        "employment", "job", "jobs", "career", "careers",
        "livelihood", "livelihoods", "unemployment", "placement",
        "wage", "wages", "worker", "workers", "skill development",
        "employability", "income opportunity",
    ],
    "ENERGY": [
        "energy", "electricity", "power supply", "power outage",
        "outage", "grid", "solar", "renewable energy", "transformer",
        "street lighting", "street light", "electric supply",
    ],
    "ENVIRONMENT": [
        "environment", "pollution", "air quality", "deforestation",
        "forest", "biodiversity", "ecosystem", "climate",
        "plastic pollution", "ecological", "conservation",
    ],
    "HEALTHCARE": [
        "health", "healthcare", "hospital", "hospitals", "clinic",
        "clinics", "doctor", "doctors", "medicine", "medical",
        "disease", "treatment", "ambulance", "maternal health",
    ],
    "INFRASTRUCTURE": [
        "infrastructure", "road", "roads", "bridge", "bridges",
        "building", "buildings", "school infrastructure",
        "drainage infrastructure", "public infrastructure",
        "facility", "facilities", "physical infrastructure",
    ],
    "OTHER": [],
    "PUBLIC_SAFETY": [
        "public safety", "unsafe", "safety", "crime", "accident",
        "street safety", "emergency communication", "security",
        "police", "lighting for safety", "road safety",
    ],
    "SANITATION": [
        "sanitation", "toilet", "toilets", "sewage", "sewer",
        "sewerage", "hygiene", "open defecation", "wastewater",
    ],
    "SOCIAL_WELFARE": [
        "social welfare", "pension", "elderly", "disability",
        "disabled", "self-help group", "vulnerable", "benefits",
        "social protection", "widow", "welfare scheme",
    ],
    "TRANSPORTATION": [
        "transport", "transportation", "public transport",
        "bus", "buses", "rail", "railway", "traffic", "mobility",
        "commute", "commuter", "road transport",
    ],
    "WASTE_MANAGEMENT": [
        "waste", "garbage", "solid waste", "waste collection",
        "waste disposal", "dumping", "landfill", "recycling",
        "segregation", "litter",
    ],
    "WATER": [
        "water", "drinking water", "water supply", "water shortage",
        "water scarcity", "groundwater", "water quality",
        "pipeline", "irrigation water",
    ],
}


# Strong cross-category overlaps worth manual review.
AMBIGUOUS_PAIRS = {
    frozenset({"EDUCATION", "EMPLOYMENT"}),
    frozenset({"PUBLIC_SAFETY", "ENERGY"}),
    frozenset({"PUBLIC_SAFETY", "DISASTER_MANAGEMENT"}),
    frozenset({"ENERGY", "DISASTER_MANAGEMENT"}),
    frozenset({"INFRASTRUCTURE", "EDUCATION"}),
    frozenset({"INFRASTRUCTURE", "TRANSPORTATION"}),
    frozenset({"ENVIRONMENT", "WASTE_MANAGEMENT"}),
    frozenset({"WATER", "SANITATION"}),
}


def clean(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_text(row: dict[str, str]) -> str:
    fields = [
        row.get("title"),
        row.get("description"),
        row.get("problem_context"),
        row.get("citizen_statement"),
    ]
    return " ".join(clean(x) for x in fields if clean(x))


def matched_signals(text: str, category: str) -> list[str]:
    normalized = normalize(text)
    return [
        signal
        for signal in CATEGORY_SIGNALS.get(category, [])
        if signal in normalized
    ]


def all_category_matches(text: str) -> dict[str, list[str]]:
    matches = {}
    for category in CATEGORY_SIGNALS:
        signals = matched_signals(text, category)
        if signals:
            matches[category] = signals
    return matches


def is_template_artifact(text: str) -> bool:
    """
    Detect wording that looks explicitly generated for evaluation.
    This is a review flag, not an automatic rejection.
    """
    normalized = normalize(text)

    template_phrases = [
        "test whether a model generalizes",
        "geographic generalization",
        "independent geographic testing",
        "local evidence should be checked before routing",
        "verify locally rather than assumed",
        "without relying on the training narrative",
        "the purpose is to test",
        "this scenario must be verified",
    ]

    return any(
        phrase in normalized
        for phrase in template_phrases
    )


def main() -> None:
    print("=" * 80)
    print("SOCIETAL INNOVATION PLATFORM")
    print("CATEGORY LABEL CONSISTENCY AUDIT")
    print("=" * 80)

    if not MASTER_FILE.exists():
        raise FileNotFoundError(
            f"Master dataset not found:\n{MASTER_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nMaster:")
    print(MASTER_FILE)

    category_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    suspicious_rows: list[dict[str, str]] = []

    signal_conflicts = 0
    template_flags = 0
    multi_category_flags = 0
    total_rows = 0

    with MASTER_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as source:

        reader = csv.DictReader(source)

        required = {
            "record_id",
            "challenge_id",
            "primary_category",
            "title",
            "description",
            "problem_context",
            "citizen_statement",
            "state",
            "district",
            "language",
        }

        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(
                f"Master dataset missing columns: {sorted(missing)}"
            )

        for row in reader:
            total_rows += 1

            record_id = clean(row.get("record_id"))
            challenge_id = clean(row.get("challenge_id"))
            category = clean(row.get("primary_category"))
            text = build_text(row)

            category_counts[category] += 1

            matches = all_category_matches(text)
            matched_categories = sorted(matches)

            # ------------------------------------------------
            # Flag 1: multiple strong category signals
            # ------------------------------------------------
            multi_category = len(matched_categories) >= 2

            # ------------------------------------------------
            # Flag 2: assigned category has no recognized signal
            # Only a heuristic because OTHER and some subtle
            # cases naturally have weak lexical signals.
            # ------------------------------------------------
            assigned_signals = matches.get(category, [])
            no_assigned_signal = (
                category != "OTHER"
                and len(assigned_signals) == 0
            )

            # ------------------------------------------------
            # Flag 3: known ambiguous semantic pair
            # ------------------------------------------------
            ambiguous_pair = ""
            for other_category in matched_categories:
                if other_category == category:
                    continue

                pair = frozenset({category, other_category})
                if pair in AMBIGUOUS_PAIRS:
                    ambiguous_pair = (
                        f"{category} <-> {other_category}"
                    )
                    pair_counts[(category, other_category)] += 1
                    break

            # ------------------------------------------------
            # Flag 4: generated/evaluation template wording
            # ------------------------------------------------
            template_flag = is_template_artifact(text)

            flags = []

            if multi_category:
                flags.append("MULTIPLE_CATEGORY_SIGNALS")

            if no_assigned_signal:
                flags.append("NO_ASSIGNED_CATEGORY_SIGNAL")

            if ambiguous_pair:
                flags.append("KNOWN_AMBIGUOUS_PAIR")

            if template_flag:
                flags.append("EVALUATION_TEMPLATE_LANGUAGE")

            if flags:
                if multi_category:
                    multi_category_flags += 1

                if no_assigned_signal:
                    signal_conflicts += 1

                if template_flag:
                    template_flags += 1

                suspicious_rows.append(
                    {
                        "record_id": record_id,
                        "challenge_id": challenge_id,
                        "primary_category": category,
                        "state": clean(row.get("state")),
                        "district": clean(row.get("district")),
                        "language": clean(row.get("language")),
                        "flags": "|".join(flags),
                        "matched_categories": "|".join(
                            matched_categories
                        ),
                        "assigned_category_signals": "|".join(
                            assigned_signals
                        ),
                        "ambiguous_pair": ambiguous_pair,
                        "title": clean(row.get("title")),
                        "description": clean(row.get("description")),
                        "problem_context": clean(
                            row.get("problem_context")
                        ),
                        "citizen_statement": clean(
                            row.get("citizen_statement")
                        ),
                    }
                )

    # ========================================================
    # WRITE REVIEW CSV
    # ========================================================

    review_fields = [
        "record_id",
        "challenge_id",
        "primary_category",
        "state",
        "district",
        "language",
        "flags",
        "matched_categories",
        "assigned_category_signals",
        "ambiguous_pair",
        "title",
        "description",
        "problem_context",
        "citizen_statement",
    ]

    with REVIEW_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as target:

        writer = csv.DictWriter(
            target,
            fieldnames=review_fields,
        )

        writer.writeheader()
        writer.writerows(suspicious_rows)

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = {
        "total_rows": total_rows,
        "category_distribution": dict(
            sorted(category_counts.items())
        ),
        "suspicious_rows": len(suspicious_rows),
        "suspicious_rate": (
            len(suspicious_rows) / total_rows
            if total_rows
            else 0.0
        ),
        "multi_category_signal_rows": multi_category_flags,
        "no_assigned_category_signal_rows": signal_conflicts,
        "evaluation_template_language_rows": template_flags,
        "known_ambiguous_pair_rows": dict(
            (
                f"{left} -> {right}",
                count,
            )
            for (left, right), count
            in sorted(pair_counts.items())
        ),
        "review_note": (
            "This audit is heuristic. It identifies records for "
            "manual review and does not automatically modify labels."
        ),
    }

    with SUMMARY_FILE.open(
        "w",
        encoding="utf-8",
    ) as target:

        json.dump(
            summary,
            target,
            indent=2,
        )

    # ========================================================
    # CONSOLE OUTPUT
    # ========================================================

    print("\n" + "=" * 80)
    print("AUDIT RESULTS")
    print("=" * 80)

    print(f"Total rows                         : {total_rows:,}")
    print(
        f"Suspicious rows                    : "
        f"{len(suspicious_rows):,}"
    )
    print(
        f"Suspicious rate                    : "
        f"{summary['suspicious_rate']:.2%}"
    )
    print(
        f"Multiple category signal rows      : "
        f"{multi_category_flags:,}"
    )
    print(
        f"No assigned-category signal rows   : "
        f"{signal_conflicts:,}"
    )
    print(
        f"Evaluation-template language rows  : "
        f"{template_flags:,}"
    )

    print("\nCategory distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category:22s} {count:>7,}")

    print("\nKnown ambiguous pair flags:")
    if pair_counts:
        for (left, right), count in sorted(
            pair_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            print(
                f"  {left} <-> {right}: {count:,}"
            )
    else:
        print("  None detected.")

    print("\nArtifacts created:")
    print(REVIEW_FILE)
    print(SUMMARY_FILE)

    print("\n" + "=" * 80)
    print("CATEGORY LABEL AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()