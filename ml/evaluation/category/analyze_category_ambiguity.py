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
    / "ambiguity_analysis"
)

PAIR_FILE = OUTPUT_DIR / "category_pair_overlap.csv"
POLICY_FILE = OUTPUT_DIR / "category_policy_review.csv"
SUMMARY_FILE = OUTPUT_DIR / "ambiguity_analysis_summary.json"


# ============================================================
# CATEGORY SIGNALS
#
# Review heuristics only. No labels are changed.
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


# ============================================================
# DOMAIN POLICY FRAMEWORK
#
# Human-review guidance, NOT automatic relabeling.
# ============================================================

POLICY_RULES = [
    {
        "pair": "EDUCATION <-> EMPLOYMENT",
        "primary_decision_rule": (
            "Use EDUCATION when the core outcome is learning, access to "
            "education, teachers, schools, training quality, or credentials. "
            "Use EMPLOYMENT when the core outcome is jobs, placement, "
            "income, livelihoods, hiring, wages, or workforce access."
        ),
        "priority_question": "What outcome is being improved: learning or employment?",
    },
    {
        "pair": "INFRASTRUCTURE <-> EDUCATION",
        "primary_decision_rule": (
            "Use INFRASTRUCTURE when the core intervention is a physical "
            "asset/facility. Use EDUCATION when the core intervention is "
            "teaching, learning, access, curriculum, or educational service quality."
        ),
        "priority_question": "Is the main intervention a physical asset or an educational outcome?",
    },
    {
        "pair": "INFRASTRUCTURE <-> TRANSPORTATION",
        "primary_decision_rule": (
            "Use INFRASTRUCTURE for construction/condition of roads, bridges, "
            "buildings, or physical facilities. Use TRANSPORTATION when the "
            "primary issue is mobility, public transit, traffic, routing, or access."
        ),
        "priority_question": "Is the problem the asset itself or movement through the system?",
    },
    {
        "pair": "WATER <-> SANITATION",
        "primary_decision_rule": (
            "Use WATER for supply, availability, access, distribution, or "
            "water quality. Use SANITATION for toilets, sewage, wastewater, "
            "hygiene, or fecal contamination."
        ),
        "priority_question": "Is the core service water supply/quality or sanitation/hygiene?",
    },
    {
        "pair": "PUBLIC_SAFETY <-> ENERGY",
        "primary_decision_rule": (
            "Use ENERGY when electricity generation, supply, reliability, "
            "grid infrastructure, or energy efficiency is the main problem. "
            "Use PUBLIC_SAFETY when the energy-enabled asset is primarily "
            "being discussed for safety/security outcomes."
        ),
        "priority_question": "Is the desired outcome reliable energy or safer public space?",
    },
    {
        "pair": "PUBLIC_SAFETY <-> DISASTER_MANAGEMENT",
        "primary_decision_rule": (
            "Use DISASTER_MANAGEMENT when the trigger is a natural/major hazard "
            "or disaster response, evacuation, relief, rescue, or preparedness. "
            "Use PUBLIC_SAFETY for ongoing everyday safety, security, crime, "
            "accident prevention, or emergency communication outside a specific disaster."
        ),
        "priority_question": "Is this a disaster/hazard lifecycle problem or an everyday safety problem?",
    },
    {
        "pair": "ENERGY <-> DISASTER_MANAGEMENT",
        "primary_decision_rule": (
            "Use ENERGY when energy reliability or infrastructure is the core "
            "problem. Use DISASTER_MANAGEMENT when a hazard/disaster and its "
            "response are the core problem, even if electricity is affected."
        ),
        "priority_question": "What is the primary intervention target: energy system or disaster response?",
    },
    {
        "pair": "ENVIRONMENT <-> WASTE_MANAGEMENT",
        "primary_decision_rule": (
            "Use WASTE_MANAGEMENT when collection, disposal, segregation, "
            "recycling, or waste logistics is the core service problem. "
            "Use ENVIRONMENT when the broader ecological/pollution outcome is primary."
        ),
        "priority_question": "Is waste service delivery the target, or the broader environmental outcome?",
    },
]


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


def category_matches(text: str) -> dict[str, list[str]]:
    results = {}
    for category in CATEGORY_SIGNALS:
        signals = matched_signals(text, category)
        if signals:
            results[category] = signals
    return results


def canonical_pair(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def main() -> None:
    print("=" * 80)
    print("SOCIETAL INNOVATION PLATFORM")
    print("CATEGORY AMBIGUITY ANALYSIS")
    print("=" * 80)

    if not MASTER_FILE.exists():
        raise FileNotFoundError(
            f"Master dataset not found:\n{MASTER_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    category_counts: Counter[str] = Counter()
    category_signal_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    assigned_pair_counts: Counter[tuple[str, str]] = Counter()
    no_signal_counts: Counter[str] = Counter()
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
        }

        missing = required - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(
                f"Master dataset missing columns: {sorted(missing)}"
            )

        for row in reader:
            total_rows += 1

            assigned = clean(row.get("primary_category"))
            text = build_text(row)

            category_counts[assigned] += 1

            matches = category_matches(text)

            for category in matches:
                category_signal_counts[category] += 1

            if assigned not in matches and assigned != "OTHER":
                no_signal_counts[assigned] += 1

            matched_categories = sorted(matches)

            for i, left in enumerate(matched_categories):
                for right in matched_categories[i + 1:]:
                    pair = canonical_pair(left, right)
                    pair_counts[pair] += 1

            # Count overlaps involving the assigned label.
            for other in matched_categories:
                if other != assigned:
                    assigned_pair_counts[
                        canonical_pair(assigned, other)
                    ] += 1

    # ========================================================
    # PAIR OVERLAP TABLE
    # ========================================================

    pair_rows = []

    for (left, right), count in pair_counts.most_common():
        left_total = category_counts[left]
        right_total = category_counts[right]

        # P(pair | left) and P(pair | right) are approximate
        # signal-cooccurrence rates, based on heuristic matches.
        left_rate = count / left_total if left_total else 0.0
        right_rate = count / right_total if right_total else 0.0

        pair_rows.append(
            {
                "category_a": left,
                "category_b": right,
                "cooccurrence_rows": count,
                "rate_within_category_a": round(left_rate, 6),
                "rate_within_category_b": round(right_rate, 6),
            }
        )

    with PAIR_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as target:

        fieldnames = [
            "category_a",
            "category_b",
            "cooccurrence_rows",
            "rate_within_category_a",
            "rate_within_category_b",
        ]

        writer = csv.DictWriter(
            target,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(pair_rows)

    # ========================================================
    # POLICY REVIEW TABLE
    # ========================================================

    policy_rows = []

    for rule in POLICY_RULES:
        left, right = rule["pair"].split(" <-> ")

        pair = canonical_pair(left, right)

        policy_rows.append(
            {
                "pair": rule["pair"],
                "observed_cooccurrence_rows": pair_counts.get(
                    pair,
                    0,
                ),
                "assigned_pair_overlap_rows": assigned_pair_counts.get(
                    pair,
                    0,
                ),
                "priority_question": rule["priority_question"],
                "primary_decision_rule": rule["primary_decision_rule"],
            }
        )

    with POLICY_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as target:

        fieldnames = [
            "pair",
            "observed_cooccurrence_rows",
            "assigned_pair_overlap_rows",
            "priority_question",
            "primary_decision_rule",
        ]

        writer = csv.DictWriter(
            target,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(policy_rows)

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = {
        "total_rows": total_rows,
        "category_distribution": dict(
            sorted(category_counts.items())
        ),
        "category_signal_counts": dict(
            sorted(category_signal_counts.items())
        ),
        "no_assigned_category_signal_counts": dict(
            sorted(no_signal_counts.items())
        ),
        "top_cooccurring_pairs": [
            {
                "category_a": left,
                "category_b": right,
                "rows": count,
            }
            for (left, right), count in pair_counts.most_common(25)
        ],
        "policy_pairs_analyzed": len(POLICY_RULES),
        "interpretation": (
            "Cooccurrence counts are heuristic lexical signals, not proof "
            "of incorrect labels. Use the policy table to guide human label review."
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
    # CONSOLE
    # ========================================================

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print(f"Total rows: {total_rows:,}")

    print("\nTop category signal co-occurrences:")
    for (left, right), count in pair_counts.most_common(15):
        print(
            f"  {left:22s} <-> {right:22s} "
            f"{count:>6,}"
        )

    print("\nRows with no lexical signal for assigned category:")
    for category, count in sorted(
        no_signal_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(
            f"  {category:22s} {count:>6,}"
        )

    print("\nArtifacts:")
    print(PAIR_FILE)
    print(POLICY_FILE)
    print(SUMMARY_FILE)

    print("\n" + "=" * 80)
    print("CATEGORY AMBIGUITY ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
