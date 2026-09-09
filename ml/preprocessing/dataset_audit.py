from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path


# ============================================================
# PROJECT / DATASET PATHS
# ============================================================

# Current file:
#
# E:\societal-innovation-platorm\ml\preprocessing\dataset_audit.py
#
# parents[0] -> preprocessing
# parents[1] -> ml
# parents[2] -> project root

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_ROOT = PROJECT_ROOT / "ml" / "data"

DATA_ROOT = Path(
    os.environ.get(
        "DATA_ROOT",
        str(DEFAULT_DATA_ROOT),
    )
).resolve()


# Actual project structure
MASTER_DIR = DATA_ROOT / "master"
TRAINING_VIEWS_DIR = DATA_ROOT / "training_views"
INSTRUCTION_DIR = DATA_ROOT / "instruction"
SPLITS_DIR = DATA_ROOT / "splits"
HOLDOUT_DIR = DATA_ROOT / "holdout"
DEDUP_DIR = DATA_ROOT / "deduplication"
METADATA_DIR = DATA_ROOT / "metadata"


MASTER_CSV = (
    MASTER_DIR / "societal_challenges_master_v2.csv"
)

MASTER_JSONL = (
    MASTER_DIR / "societal_challenges_master_v2.jsonl"
)


EXPECTED_SPLITS = {
    "train_v2.csv": SPLITS_DIR / "train_v2.csv",
    "validation_v2.csv": SPLITS_DIR / "validation_v2.csv",
    "test_v2.csv": SPLITS_DIR / "test_v2.csv",
    "geographic_holdout_test_v2.csv": (
        HOLDOUT_DIR / "geographic_holdout_test_v2.csv"
    ),
}


EXPECTED_CATEGORIES = {
    "WATER",
    "SANITATION",
    "WASTE_MANAGEMENT",
    "HEALTHCARE",
    "EDUCATION",
    "AGRICULTURE",
    "TRANSPORTATION",
    "ENERGY",
    "ENVIRONMENT",
    "PUBLIC_SAFETY",
    "INFRASTRUCTURE",
    "DIGITAL_SERVICES",
    "EMPLOYMENT",
    "SOCIAL_WELFARE",
    "DISASTER_MANAGEMENT",
    "OTHER",
}


EXPECTED_SEVERITIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


EXPECTED_URGENCIES = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
}


EXPECTED_ROUTING_TYPES = {
    "MUNICIPALITY",
    "GOVERNMENT",
    "INNOVATION",
    "HUMAN_REVIEW",
}


# ============================================================
# OUTPUT / DISPLAY HELPERS
# ============================================================

def print_header(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_warning(message: str) -> None:
    print(f"[WARN] {message}")


def print_pass(message: str) -> None:
    print(f"[PASS] {message}")


def print_fail(message: str) -> None:
    print(f"[FAIL] {message}")


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: str) -> str:
    """
    Normalize text for duplicate/leakage analysis.

    Removes:
    - synthetic case markers
    - synthetic record identifiers
    - excessive whitespace
    - punctuation differences

    Preserves:
    - English letters
    - digits
    - Devanagari characters
    """

    if not value:
        return ""

    text = str(value).lower()

    # Remove:
    # "record marker case-abcdef"
    # "record mark: case-abcdef"
    text = re.sub(
        r"\brecord\s+(?:marker|mark)\s*:?\s*case-[a-z0-9_-]+\b",
        " ",
        text,
    )

    # Remove standalone synthetic case IDs.
    text = re.sub(
        r"\bcase-[a-z0-9_-]{6,}\b",
        " ",
        text,
    )

    # Remove common synthetic record IDs.
    text = re.sub(
        r"\b(?:ut|syn|record)[-_]?\d{2,}[-_a-z0-9]*\b",
        " ",
        text,
    )

    # Keep:
    # English a-z
    # digits
    # Hindi / Devanagari
    text = re.sub(
        r"[^a-z0-9\u0900-\u097f]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def fingerprint(value: str) -> str:
    normalized = normalize_text(value)

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def row_fingerprint(row: dict[str, str]) -> str:
    """
    Create a deterministic fingerprint for a complete CSV row.
    """

    canonical = "\x1f".join(
        str(row.get(column, "")).strip()
        for column in sorted(row)
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def duplicate_excess(counter: Counter) -> int:
    """
    Example:
        A A A B B C

    Duplicate excess:
        2 + 1 = 3
    """

    return sum(
        count - 1
        for count in counter.values()
        if count > 1
    )


# ============================================================
# DIRECTORY AUDIT
# ============================================================

def audit_directories() -> dict:
    print_header("DIRECTORY CHECK")

    directories = {
        "DATA_ROOT": DATA_ROOT,
        "MASTER": MASTER_DIR,
        "TRAINING_VIEWS": TRAINING_VIEWS_DIR,
        "INSTRUCTION": INSTRUCTION_DIR,
        "SPLITS": SPLITS_DIR,
        "HOLDOUT": HOLDOUT_DIR,
        "DEDUPLICATION": DEDUP_DIR,
        "METADATA": METADATA_DIR,
    }

    results = {}

    for name, path in directories.items():

        exists = path.exists()

        results[name] = {
            "path": str(path),
            "exists": exists,
        }

        print(
            f"{name:<20}"
            f"{'PASS' if exists else 'FAIL'}"
        )

        print(f"  {path}")

    return results


# ============================================================
# MASTER DATASET AUDIT
# ============================================================

def audit_master() -> dict:
    print_header("MASTER DATASET")

    if not MASTER_CSV.exists():
        raise FileNotFoundError(
            f"Master CSV not found:\n{MASTER_CSV}"
        )

    rows = 0
    columns: list[str] = []

    record_ids = set()
    challenge_ids = set()

    duplicate_record_ids = Counter()
    duplicate_challenge_ids = Counter()

    exact_row_hashes = Counter()
    exact_descriptions = Counter()
    normalized_descriptions = Counter()
    title_description_hashes = Counter()

    categories = Counter()
    states = Counter()
    districts = Counter()
    languages = Counter()
    severity = Counter()
    urgency = Counter()
    routing = Counter()
    innovation = Counter()

    missing_values = Counter()

    title_lengths = []
    description_lengths = []

    with MASTER_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        columns = reader.fieldnames or []

        if not columns:
            raise RuntimeError(
                "Master CSV contains no header."
            )

        # Only genuinely essential fields are required here.
        required_columns = {
            "record_id",
            "challenge_id",
            "title",
            "description",
            "state",
            "language",
            "severity",
            "urgency",
            "innovation_required",
            "routing_type",
        }

        missing_required = (
            required_columns - set(columns)
        )

        if missing_required:

            print_fail(
                "Missing essential master columns:"
            )

            for column in sorted(
                missing_required
            ):
                print(
                    f"  {column}"
                )

        category_column = None

        if "primary_category" in columns:
            category_column = "primary_category"

        elif "category" in columns:
            category_column = "category"

        else:
            print_warning(
                "No category / primary_category "
                "column exists in master CSV."
            )

        for row in reader:

            rows += 1

            record_id = (
                row.get("record_id", "")
                or ""
            ).strip()

            challenge_id = (
                row.get("challenge_id", "")
                or ""
            ).strip()

            # -----------------------------------------------
            # Record IDs
            # -----------------------------------------------

            if record_id in record_ids:
                duplicate_record_ids[
                    record_id
                ] += 1

            if record_id:
                record_ids.add(record_id)

            # -----------------------------------------------
            # Challenge IDs
            # -----------------------------------------------

            if challenge_id in challenge_ids:
                duplicate_challenge_ids[
                    challenge_id
                ] += 1

            if challenge_id:
                challenge_ids.add(challenge_id)

            # -----------------------------------------------
            # Complete-row duplicate
            # -----------------------------------------------

            exact_row_hashes[
                row_fingerprint(row)
            ] += 1

            # -----------------------------------------------
            # Description duplication
            # -----------------------------------------------

            description = (
                row.get("description", "")
                or ""
            ).strip()

            exact_descriptions[
                description
            ] += 1

            normalized_description = normalize_text(
                description
            )

            if normalized_description:
                normalized_descriptions[
                    normalized_description
                ] += 1

            # -----------------------------------------------
            # Title + description duplication
            # -----------------------------------------------

            title = (
                row.get("title", "")
                or ""
            ).strip()

            title_description_hashes[
                fingerprint(
                    f"{title} | {description}"
                )
            ] += 1

            # -----------------------------------------------
            # Categories
            # -----------------------------------------------

            if category_column:

                categories[
                    (
                        row.get(
                            category_column,
                            "",
                        )
                        or ""
                    ).strip()
                ] += 1

            # -----------------------------------------------
            # Other distributions
            # -----------------------------------------------

            states[
                (
                    row.get("state", "")
                    or ""
                ).strip()
            ] += 1

            districts[
                (
                    row.get("district", "")
                    or ""
                ).strip()
            ] += 1

            languages[
                (
                    row.get("language", "")
                    or ""
                ).strip()
            ] += 1

            severity[
                (
                    row.get("severity", "")
                    or ""
                ).strip()
            ] += 1

            urgency[
                (
                    row.get("urgency", "")
                    or ""
                ).strip()
            ] += 1

            routing[
                (
                    row.get("routing_type", "")
                    or ""
                ).strip()
            ] += 1

            innovation[
                (
                    row.get(
                        "innovation_required",
                        "",
                    )
                    or ""
                ).strip().lower()
            ] += 1

            # -----------------------------------------------
            # Missing values
            # -----------------------------------------------

            for column in columns:

                value = row.get(column)

                if (
                    value is None
                    or not str(value).strip()
                ):
                    missing_values[column] += 1

            # -----------------------------------------------
            # Text length
            # -----------------------------------------------

            title_lengths.append(
                len(title)
            )

            description_lengths.append(
                len(description)
            )

    # ========================================================
    # Calculations
    # ========================================================

    exact_duplicate_rows = (
        duplicate_excess(
            exact_row_hashes
        )
    )

    duplicate_description_rows = (
        duplicate_excess(
            exact_descriptions
        )
    )

    normalized_duplicate_rows = (
        duplicate_excess(
            normalized_descriptions
        )
    )

    title_description_duplicates = (
        duplicate_excess(
            title_description_hashes
        )
    )

    present_categories = {
        value.strip()
        for value in categories
        if value.strip()
    }

    missing_categories = (
        EXPECTED_CATEGORIES
        - present_categories
    )

    # ========================================================
    # Display
    # ========================================================

    print(
        f"File: {MASTER_CSV}"
    )

    print(
        f"Rows: {rows:,}"
    )

    print(
        f"Columns: {len(columns):,}"
    )

    print(
        f"Unique record IDs: "
        f"{len(record_ids):,}"
    )

    print(
        f"Unique challenge IDs: "
        f"{len(challenge_ids):,}"
    )

    print(
        f"Exact duplicate FULL rows: "
        f"{exact_duplicate_rows:,}"
    )

    print(
        f"Duplicate descriptions: "
        f"{duplicate_description_rows:,}"
    )

    print(
        f"Normalized duplicate descriptions: "
        f"{normalized_duplicate_rows:,}"
    )

    print(
        f"Title + description duplicates: "
        f"{title_description_duplicates:,}"
    )

    print(
        f"\nCategory column: "
        f"{category_column or 'NOT FOUND'}"
    )

    if category_column:

        print("\nPRIMARY CATEGORY DISTRIBUTION:")

        for category, count in (
            categories.most_common()
        ):
            print(
                f"  {category}: {count:,}"
            )

        print("\nMISSING CATEGORIES:")

        if missing_categories:

            for category in sorted(
                missing_categories
            ):
                print(
                    f"  {category}"
                )

        else:
            print("  None")

    print("\nSTATE DISTRIBUTION:")

    for state, count in (
        states.most_common()
    ):
        print(
            f"  {state}: {count:,}"
        )

    print("\nLANGUAGE DISTRIBUTION:")

    for language, count in (
        languages.most_common()
    ):
        print(
            f"  {language}: {count:,}"
        )

    print("\nSEVERITY DISTRIBUTION:")

    for label, count in (
        severity.most_common()
    ):
        print(
            f"  {label}: {count:,}"
        )

    print("\nURGENCY DISTRIBUTION:")

    for label, count in (
        urgency.most_common()
    ):
        print(
            f"  {label}: {count:,}"
        )

    print("\nROUTING DISTRIBUTION:")

    for label, count in (
        routing.most_common()
    ):
        print(
            f"  {label}: {count:,}"
        )

    print("\nINNOVATION DISTRIBUTION:")

    for label, count in (
        innovation.most_common()
    ):
        print(
            f"  {label}: {count:,}"
        )

    print("\nTOP MISSING FIELDS:")

    for field, count in (
        missing_values.most_common(30)
    ):

        percentage = (
            count / rows * 100
            if rows
            else 0
        )

        print(
            f"  {field}: "
            f"{count:,} "
            f"({percentage:.2f}%)"
        )

    if title_lengths:

        print("\nTEXT STATISTICS:")

        print(
            f"  Average title length: "
            f"{sum(title_lengths) / len(title_lengths):.2f}"
        )

        print(
            f"  Minimum title length: "
            f"{min(title_lengths)}"
        )

        print(
            f"  Maximum title length: "
            f"{max(title_lengths)}"
        )

        print(
            f"  Average description length: "
            f"{sum(description_lengths) / len(description_lengths):.2f}"
        )

        print(
            f"  Minimum description length: "
            f"{min(description_lengths)}"
        )

        print(
            f"  Maximum description length: "
            f"{max(description_lengths)}"
        )

    return {
        "file": str(MASTER_CSV),
        "rows": rows,
        "columns": len(columns),
        "column_names": columns,
        "unique_record_ids": len(record_ids),
        "unique_challenge_ids": len(challenge_ids),
        "duplicate_record_ids": sum(
            duplicate_record_ids.values()
        ),
        "duplicate_challenge_ids": sum(
            duplicate_challenge_ids.values()
        ),
        "exact_duplicate_full_rows": (
            exact_duplicate_rows
        ),
        "duplicate_descriptions": (
            duplicate_description_rows
        ),
        "normalized_duplicate_descriptions": (
            normalized_duplicate_rows
        ),
        "title_description_duplicates": (
            title_description_duplicates
        ),
        "category_column": category_column,
        "categories": dict(categories),
        "missing_categories": sorted(
            missing_categories
        ),
        "states": dict(states),
        "districts": dict(districts),
        "languages": dict(languages),
        "severity": dict(severity),
        "urgency": dict(urgency),
        "routing": dict(routing),
        "innovation_required": dict(
            innovation
        ),
        "missing_values": dict(
            missing_values
        ),
    }


# ============================================================
# CSV INVENTORY
# ============================================================

def audit_csv_file(path: Path) -> dict:

    if not path.exists():

        print_fail(
            f"{path.name}: MISSING"
        )

        return {
            "exists": False,
            "rows": 0,
            "columns": 0,
        }

    rows = 0
    columns = 0
    header = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.reader(file)

        try:
            header = next(reader)
            columns = len(header)

        except StopIteration:

            header = []

        for _ in reader:
            rows += 1

    print(
        f"{path.name}: "
        f"{rows:,} rows, "
        f"{columns:,} columns"
    )

    return {
        "exists": True,
        "rows": rows,
        "columns": columns,
        "column_names": header,
    }


# ============================================================
# TRAINING VIEWS
# ============================================================

def audit_training_views() -> dict:

    print_header(
        "TRAINING VIEWS"
    )

    results = {}

    expected = [
        "triage_training_v2.csv",
        "impact_prediction_v2.csv",
        "university_matching_v2.csv",
        "industry_matching_v2.csv",
    ]

    for filename in expected:

        path = (
            TRAINING_VIEWS_DIR
            / filename
        )

        results[filename] = audit_csv_file(
            path
        )

    return results


# ============================================================
# SPLITS
# ============================================================

def audit_splits() -> dict:

    print_header(
        "TRAIN / VALIDATION / TEST / HOLDOUT"
    )

    results = {}

    for name, path in EXPECTED_SPLITS.items():

        print(
            f"\n{name}"
        )

        results[name] = audit_csv_file(
            path
        )

    return results


# ============================================================
# SPLIT LEAKAGE
# ============================================================

def load_split(path: Path) -> dict | None:

    if not path.exists():
        return None

    record_ids = set()
    challenge_ids = set()
    titles = set()
    descriptions = set()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            record_id = (
                row.get("record_id", "")
                or ""
            ).strip()

            challenge_id = (
                row.get("challenge_id", "")
                or ""
            ).strip()

            title = normalize_text(
                row.get("title", "")
                or ""
            )

            description = normalize_text(
                row.get("description", "")
                or ""
            )

            if record_id:
                record_ids.add(
                    record_id
                )

            if challenge_id:
                challenge_ids.add(
                    challenge_id
                )

            if title:
                titles.add(title)

            if description:
                descriptions.add(
                    description
                )

    return {
        "record_ids": record_ids,
        "challenge_ids": challenge_ids,
        "titles": titles,
        "descriptions": descriptions,
    }


def audit_leakage() -> dict:

    print_header(
        "SPLIT LEAKAGE"
    )

    datasets = {}

    for name, path in EXPECTED_SPLITS.items():

        data = load_split(path)

        if data is None:

            print_warning(
                f"{name} not found."
            )

            continue

        datasets[name] = data

        print(
            f"{name}: "
            f"{len(data['challenge_ids']):,} challenge IDs"
        )

        print(
            f"  Record IDs: "
            f"{len(data['record_ids']):,}"
        )

        print(
            f"  Unique normalized titles: "
            f"{len(data['titles']):,}"
        )

        print(
            f"  Unique normalized descriptions: "
            f"{len(data['descriptions']):,}"
        )

    has_id_leakage = False
    has_record_id_leakage = False
    has_title_leakage = False
    has_description_leakage = False

    pairs = {}

    names = list(datasets)

    for i in range(len(names)):

        for j in range(i + 1, len(names)):

            left_name = names[i]
            right_name = names[j]

            left = datasets[left_name]
            right = datasets[right_name]

            id_overlap = (
                left["challenge_ids"]
                & right["challenge_ids"]
            )

            record_overlap = (
                left["record_ids"]
                & right["record_ids"]
            )

            title_overlap = (
                left["titles"]
                & right["titles"]
            )

            description_overlap = (
                left["descriptions"]
                & right["descriptions"]
            )

            pair = (
                f"{left_name} vs {right_name}"
            )

            pairs[pair] = {
                "challenge_id_overlap": len(
                    id_overlap
                ),
                "record_id_overlap": len(
                    record_overlap
                ),
                "title_overlap": len(
                    title_overlap
                ),
                "description_overlap": len(
                    description_overlap
                ),
            }

            print(
                f"\n{pair}"
            )

            print(
                "  Challenge ID overlap:",
                len(id_overlap),
            )

            print(
                "  Record ID overlap:",
                len(record_overlap),
            )

            print(
                "  Normalized title overlap:",
                len(title_overlap),
            )

            print(
                "  Normalized description overlap:",
                len(description_overlap),
            )

            if id_overlap:
                has_id_leakage = True

            if record_overlap:
                has_record_id_leakage = True

            if title_overlap:
                has_title_leakage = True

            if description_overlap:
                has_description_leakage = True

    overall = any(
        [
            has_id_leakage,
            has_record_id_leakage,
            has_title_leakage,
            has_description_leakage,
        ]
    )

    print(
        "\nLEAKAGE STATUS:",
        "FAIL" if overall else "PASS",
    )

    return {
        "has_id_leakage": has_id_leakage,
        "has_record_id_leakage": has_record_id_leakage,
        "has_title_leakage": has_title_leakage,
        "has_description_leakage": (
            has_description_leakage
        ),
        "has_leakage": overall,
        "pairs": pairs,
    }


# ============================================================
# JSONL AUDIT
# ============================================================

def audit_jsonl_file(path: Path) -> dict:

    records = 0
    invalid = 0
    empty_lines = 0

    if not path.exists():

        print_fail(
            f"{path.name}: MISSING"
        )

        return {
            "exists": False,
            "records": 0,
            "invalid": 0,
            "empty_lines": 0,
        }

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1,
        ):

            line = line.strip()

            if not line:

                empty_lines += 1

                continue

            records += 1

            try:
                json.loads(line)

            except json.JSONDecodeError as exc:

                invalid += 1

                print_warning(
                    f"{path.name}: "
                    f"invalid JSON at line "
                    f"{line_number}: {exc}"
                )

    print(
        f"{path.name}: "
        f"{records:,} records, "
        f"{invalid:,} invalid, "
        f"{empty_lines:,} empty"
    )

    return {
        "exists": True,
        "records": records,
        "invalid": invalid,
        "empty_lines": empty_lines,
    }


def audit_jsonl_directory() -> dict:

    print_header(
        "INSTRUCTION DATASETS"
    )

    results = {}

    if not INSTRUCTION_DIR.exists():

        print_fail(
            f"Instruction directory missing: "
            f"{INSTRUCTION_DIR}"
        )

        return results

    for path in sorted(
        INSTRUCTION_DIR.glob("*.jsonl")
    ):

        results[path.name] = audit_jsonl_file(
            path
        )

    return results


def audit_master_jsonl() -> dict:

    print_header(
        "MASTER JSONL"
    )

    return audit_jsonl_file(
        MASTER_JSONL
    )


# ============================================================
# DEDUPLICATION DATASET
# ============================================================

def audit_deduplication() -> dict:

    print_header(
        "DEDUPLICATION DATASET"
    )

    path = (
        DEDUP_DIR
        / "challenge_pairs_deduplication_v2.csv"
    )

    if not path.exists():

        print_fail(
            f"Missing: {path}"
        )

        return {
            "exists": False
        }

    rows = 0
    labels = Counter()

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            rows += 1

            label = (
                row.get(
                    "semantic_similarity_label",
                    "",
                )
                or ""
            ).strip()

            if label:
                labels[label] += 1

    print(
        f"Rows: {rows:,}"
    )

    print(
        "\nSimilarity labels:"
    )

    for label, count in (
        labels.most_common()
    ):
        print(
            f"  {label}: {count:,}"
        )

    return {
        "exists": True,
        "rows": rows,
        "labels": dict(labels),
    }


# ============================================================
# UTTARAKHAND COVERAGE
# ============================================================

def audit_uttarakhand() -> dict:

    print_header(
        "UTTARAKHAND COVERAGE"
    )

    districts = Counter()
    total = 0

    with MASTER_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            state = (
                row.get("state", "")
                or ""
            ).strip().lower()

            if state == "uttarakhand":

                total += 1

                district = (
                    row.get(
                        "district",
                        "",
                    )
                    or "UNKNOWN"
                ).strip()

                districts[district] += 1

    print(
        f"Uttarakhand records: "
        f"{total:,}"
    )

    print(
        "\nDistrict distribution:"
    )

    for district, count in (
        districts.most_common()
    ):
        print(
            f"  {district}: {count:,}"
        )

    return {
        "records": total,
        "districts": dict(districts),
    }


# ============================================================
# QUALITY GATE
# ============================================================

def build_quality_gate(
    directories: dict,
    master: dict,
    master_jsonl: dict,
    leakage: dict,
    instruction: dict,
) -> dict:

    directory_status = all(
        item["exists"]
        for item in directories.values()
    )

    all_jsonl_valid = all(
        item.get("invalid", 0) == 0
        for item in instruction.values()
    )

    master_jsonl_valid = (
        master_jsonl.get("exists", False)
        and master_jsonl.get("invalid", 0) == 0
    )

    categories_valid = (
        master["category_column"] is not None
        and len(
            master["missing_categories"]
        ) == 0
    )

    return {
        "directories_present": directory_status,

        "master_has_records": (
            master["rows"] > 0
        ),

        "unique_record_ids": (
            master["unique_record_ids"]
            == master["rows"]
        ),

        "unique_challenge_ids": (
            master["unique_challenge_ids"]
            == master["rows"]
        ),

        "zero_exact_duplicate_rows": (
            master[
                "exact_duplicate_full_rows"
            ] == 0
        ),

        "all_16_categories_present": (
            categories_valid
        ),

        "master_jsonl_valid": (
            master_jsonl_valid
        ),

        "instruction_jsonl_valid": (
            all_jsonl_valid
        ),

        "no_split_id_leakage": (
            not leakage[
                "has_id_leakage"
            ]
        ),

        "no_split_record_id_leakage": (
            not leakage[
                "has_record_id_leakage"
            ]
        ),

        "no_split_title_leakage": (
            not leakage[
                "has_title_leakage"
            ]
        ),

        "no_split_description_leakage": (
            not leakage[
                "has_description_leakage"
            ]
        ),
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print_header(
        "SOCIETAL INNOVATION PLATFORM - DATASET AUDIT"
    )

    print(
        "Project root:"
    )
    print(
        PROJECT_ROOT
    )

    print(
        "\nData root:"
    )
    print(
        DATA_ROOT
    )

    # --------------------------------------------------------
    # DIRECTORY CHECK
    # --------------------------------------------------------

    directories = audit_directories()

    # --------------------------------------------------------
    # MASTER
    # --------------------------------------------------------

    master = audit_master()

    # --------------------------------------------------------
    # MASTER JSONL
    # --------------------------------------------------------

    master_jsonl = audit_master_jsonl()

    # --------------------------------------------------------
    # UTTARAKHAND
    # --------------------------------------------------------

    uttarakhand = audit_uttarakhand()

    # --------------------------------------------------------
    # TRAINING VIEWS
    # --------------------------------------------------------

    training_views = audit_training_views()

    # --------------------------------------------------------
    # SPLITS
    # --------------------------------------------------------

    splits = audit_splits()

    # --------------------------------------------------------
    # LEAKAGE
    # --------------------------------------------------------

    leakage = audit_leakage()

    # --------------------------------------------------------
    # INSTRUCTION JSONL
    # --------------------------------------------------------

    instruction = audit_jsonl_directory()

    # --------------------------------------------------------
    # DEDUPLICATION
    # --------------------------------------------------------

    deduplication = audit_deduplication()

    # --------------------------------------------------------
    # QUALITY GATE
    # --------------------------------------------------------

    gate = build_quality_gate(
        directories=directories,
        master=master,
        master_jsonl=master_jsonl,
        leakage=leakage,
        instruction=instruction,
    )

    print_header(
        "FINAL QUALITY GATE"
    )

    for name, passed in gate.items():

        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    overall = all(
        gate.values()
    )

    print(
        "\nOVERALL DATASET STATUS:",
        "PASS" if overall else "FAIL",
    )

    # --------------------------------------------------------
    # SAVE REPORT
    # --------------------------------------------------------

    METADATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "project_root": str(
            PROJECT_ROOT
        ),
        "data_root": str(
            DATA_ROOT
        ),
        "directories": directories,
        "master": master,
        "master_jsonl": master_jsonl,
        "uttarakhand": uttarakhand,
        "training_views": training_views,
        "splits": splits,
        "leakage": leakage,
        "instruction": instruction,
        "deduplication": deduplication,
        "quality_gate": gate,
        "overall_status": (
            "PASS"
            if overall
            else "FAIL"
        ),
    }

    report_path = (
        METADATA_DIR
        / "dataset_audit_report.json"
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        "\nAudit report written to:"
    )

    print(
        report_path
    )


if __name__ == "__main__":
    main()