from __future__ import annotations

import re

from app.ai.category_service import predict_category
from app.ai.schemas import (
    TriageRequest,
    TriageResponse,
    TriageRoutingType,
)


# ============================================================
# VERSION
# ============================================================

MODEL_VERSION = (
    "category-tfidf-logreg-v1"
    "+rule-triage-v0.3"
)


# ============================================================
# CATEGORY KEYWORDS
#
# These remain as fallback/secondary signals for the rest of
# the triage pipeline. Primary category prediction is now
# performed by the trained ML classifier.
# ============================================================

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "WATER": [
        "water",
        "drinking water",
        "pipeline",
        "pipe",
        "leakage",
        "water supply",
        "borewell",
        "well",
        "turbidity",
        "tank",
        "irrigation",
    ],
    "SANITATION": [
        "sanitation",
        "toilet",
        "sewage",
        "sewer",
        "drain",
        "drainage",
        "wastewater",
        "open defecation",
    ],
    "WASTE_MANAGEMENT": [
        "garbage",
        "waste",
        "dustbin",
        "dumping",
        "plastic waste",
        "solid waste",
        "litter",
    ],
    "HEALTHCARE": [
        "hospital",
        "doctor",
        "medicine",
        "medical",
        "health",
        "ambulance",
        "clinic",
        "phc",
        "blood",
        "oxygen",
        "vaccine",
        "telemedicine",
    ],
    "EDUCATION": [
        "school",
        "college",
        "student",
        "teacher",
        "education",
        "classroom",
        "textbook",
        "library",
    ],
    "AGRICULTURE": [
        "farmer",
        "crop",
        "agriculture",
        "agricultural",
        "irrigation",
        "soil",
        "pesticide",
        "fertilizer",
        "orchard",
        "harvest",
    ],
    "TRANSPORTATION": [
        "traffic",
        "bus",
        "transport",
        "parking",
        "road congestion",
        "public transport",
        "signal",
    ],
    "ENERGY": [
        "electricity",
        "power",
        "transformer",
        "grid",
        "feeder",
        "voltage",
        "solar",
        "energy",
        "substation",
    ],
    "ENVIRONMENT": [
        "pollution",
        "environment",
        "river",
        "forest",
        "air quality",
        "noise",
        "ecology",
        "water pollution",
        "tree cutting",
    ],
    "PUBLIC_SAFETY": [
        "safety",
        "crime",
        "cctv",
        "streetlight",
        "street light",
        "emergency",
        "hazard",
        "danger",
        "security",
    ],
    "INFRASTRUCTURE": [
        "bridge",
        "building",
        "road",
        "pothole",
        "footbridge",
        "culvert",
        "retaining wall",
        "infrastructure",
    ],
    "DIGITAL_SERVICES": [
        "internet",
        "website",
        "portal",
        "software",
        "application",
        "digital",
        "network",
        "server",
        "api",
        "connectivity",
    ],
    "EMPLOYMENT": [
        "employment",
        "job",
        "jobs",
        "unemployment",
        "livelihood",
        "skill development",
        "worker",
    ],
    "SOCIAL_WELFARE": [
        "pension",
        "welfare",
        "social security",
        "benefit",
        "ration",
        "disability",
        "elderly",
        "financial assistance",
    ],
    "DISASTER_MANAGEMENT": [
        "landslide",
        "flood",
        "flash flood",
        "cloudburst",
        "earthquake",
        "forest fire",
        "wildfire",
        "rockfall",
        "disaster",
        "hazard warning",
        "evacuation",
    ],
}


# ============================================================
# INNOVATION SIGNALS
# ============================================================

INNOVATION_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "sensor",
    "iot",
    "internet of things",
    "satellite",
    "drone",
    "robot",
    "robotics",
    "predictive",
    "prediction",
    "early warning system",
    "smart system",
    "computer vision",
    "remote sensing",
    "digital twin",
    "automation",
    "prototype",
    "research",
    "real-time monitoring",
]


# ============================================================
# URGENCY SIGNALS
# ============================================================

CRITICAL_KEYWORDS = [
    "death",
    "fatal",
    "critical",
    "emergency",
    "immediate danger",
    "life threatening",
    "oxygen shortage",
    "fire",
    "flash flood",
    "major landslide",
    "bridge collapse",
    "electrical hazard",
]

HIGH_URGENCY_KEYWORDS = [
    "urgent",
    "soon",
    "blocked",
    "outage",
    "shortage",
    "leak",
    "contamination",
    "danger",
    "risk",
    "failed",
    "breakdown",
]


# ============================================================
# HELPERS
# ============================================================

def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _keyword_matches(
    text: str,
    keywords: list[str],
) -> int:
    return sum(
        1
        for keyword in keywords
        if keyword in text
    )


# ============================================================
# RULE-BASED URGENCY
# ============================================================

def _calculate_urgency(
    text: str,
    request: TriageRequest,
) -> tuple[str, float, str]:

    critical_matches = _keyword_matches(
        text,
        CRITICAL_KEYWORDS,
    )

    high_matches = _keyword_matches(
        text,
        HIGH_URGENCY_KEYWORDS,
    )

    if critical_matches >= 2:
        return (
            "CRITICAL",
            0.95,
            (
                "The report contains multiple indicators "
                "of immediate or potentially life-threatening risk."
            ),
        )

    if critical_matches >= 1:
        return (
            "HIGH",
            0.85,
            (
                "The report contains an indicator requiring "
                "prompt attention."
            ),
        )

    if high_matches >= 2:
        return (
            "HIGH",
            0.75,
            (
                "The report contains multiple indicators "
                "of a time-sensitive problem."
            ),
        )

    if high_matches >= 1:
        return (
            "MEDIUM",
            0.60,
            "The problem appears to require timely attention.",
        )

    if (
        request.affected_population
        and request.affected_population >= 1000
    ):
        return (
            "MEDIUM",
            0.55,
            (
                "A relatively large affected population "
                "increases the need for timely action."
            ),
        )

    return (
        "LOW",
        0.35,
        (
            "No strong indicators of immediate "
            "time-sensitive risk were identified."
        ),
    )


# ============================================================
# RULE-BASED SEVERITY
# ============================================================

def _calculate_severity(
    request: TriageRequest,
    text: str,
    urgency: str,
) -> tuple[str, float, str]:

    affected = request.affected_population or 0
    loss = request.estimated_economic_loss or 0

    critical_matches = _keyword_matches(
        text,
        CRITICAL_KEYWORDS,
    )

    score = 0.25

    if affected >= 100:
        score += 0.15

    if affected >= 1000:
        score += 0.15

    if affected >= 10000:
        score += 0.15

    if loss >= 100000:
        score += 0.10

    if loss >= 1000000:
        score += 0.15

    if critical_matches:
        score += 0.20

    if urgency == "CRITICAL":
        score += 0.10

    score = min(score, 1.0)

    if score >= 0.80:
        severity = "CRITICAL"
    elif score >= 0.60:
        severity = "HIGH"
    elif score >= 0.40:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    reason = (
        "Severity was estimated using affected population, "
        "economic impact, risk indicators, and urgency signals. "
        f"Estimated score: {score:.2f}."
    )

    return severity, score, reason


# ============================================================
# RULE-BASED INNOVATION DETECTION
# ============================================================

def _detect_innovation(
    text: str,
) -> tuple[bool, float, str]:

    matches = _keyword_matches(
        text,
        INNOVATION_KEYWORDS,
    )

    if matches >= 2:
        return (
            True,
            min(0.55 + matches * 0.08, 0.95),
            (
                "The description contains multiple indicators "
                "of technology, research, monitoring, or "
                "engineering innovation."
            ),
        )

    if matches == 1:
        return (
            True,
            0.62,
            (
                "The description contains an indicator that "
                "a technology or research-based intervention "
                "may be useful."
            ),
        )

    return (
        False,
        0.25,
        (
            "The challenge currently appears solvable through "
            "conventional service delivery or administrative action."
        ),
    )


# ============================================================
# ROUTING
# ============================================================

def _determine_routing(
    category: str,
    innovation_required: bool,
    confidence_inputs: tuple[float, float],
    request: TriageRequest,
    category_requires_human_review: bool = False,
) -> tuple[TriageRoutingType, float, str]:

    severity_score, urgency_score = confidence_inputs

    if category_requires_human_review:
        return (
            TriageRoutingType.HUMAN_REVIEW,
            0.90,
            (
                "The category prediction is ambiguous or low-confidence. "
                "Authorized human review is required before automated routing."
            ),
        )

    if severity_score >= 0.85 and urgency_score >= 0.80:
        return (
            TriageRoutingType.HUMAN_REVIEW,
            0.86,
            (
                "The combination of high severity and urgency requires "
                "authorized human review before automated routing."
            ),
        )

    if innovation_required:
        return (
            TriageRoutingType.INNOVATION,
            0.79,
            (
                "The challenge appears to require technology, research, "
                "engineering, or an innovative intervention."
            ),
        )

    local_categories = {
        "WATER",
        "SANITATION",
        "WASTE_MANAGEMENT",
        "TRANSPORTATION",
        "INFRASTRUCTURE",
        "PUBLIC_SAFETY",
    }

    if category in local_categories:
        return (
            TriageRoutingType.MUNICIPALITY,
            0.82,
            (
                "The challenge appears suitable for local-body "
                "or municipal-level intervention."
            ),
        )

    return (
        TriageRoutingType.GOVERNMENT,
        0.74,
        (
            "The challenge appears to require government-department-level "
            "coordination or intervention."
        ),
    )


# ============================================================
# MAIN TRIAGE PIPELINE
# ============================================================

def triage_challenge(
    request: TriageRequest,
) -> TriageResponse:

    combined_text = _normalize_text(
        " ".join(
            [
                request.title,
                request.description,
                request.address or "",
                request.district or "",
                request.state or "",
            ]
        )
    )

    # --------------------------------------------------------
    # ML CATEGORY PREDICTION
    # --------------------------------------------------------

    category_result = predict_category(
        description=request.description,
        problem_context="",
        citizen_statement=request.description,
        state=request.state or "",
        district=request.district or "",
    )

    predicted_category = category_result["category"]

    category_requires_human_review = bool(
        category_result["requires_human_review"]
    )

    # If the caller explicitly supplies a category, we still use
    # the ML model to verify it. The requested category is treated
    # as user-provided context, not as a replacement for AI inference.
    requested_category = (
        request.category
        if request.category
        else None
    )

    category = predicted_category

    # --------------------------------------------------------
    # URGENCY / SEVERITY / INNOVATION
    # --------------------------------------------------------

    urgency, urgency_score, urgency_reason = _calculate_urgency(
        combined_text,
        request,
    )

    severity, severity_score, severity_reason = _calculate_severity(
        request,
        combined_text,
        urgency,
    )

    innovation_required, innovation_score, innovation_reason = (
        _detect_innovation(combined_text)
    )

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    routing_type, routing_confidence, routing_reason = (
        _determine_routing(
            category,
            innovation_required,
            (severity_score, urgency_score),
            request,
            category_requires_human_review,
        )
    )

    # --------------------------------------------------------
    # AUGMENT ROUTING REASON WITH ML CATEGORY DETAILS
    # --------------------------------------------------------

    routing_reason = (
        f"{routing_reason} "
        f"Category model confidence: "
        f"{category_result['confidence']:.2f}; "
        f"top-1/top-2 margin: "
        f"{category_result['margin']:.2f}."
    )

    if requested_category:
        routing_reason += (
            f" User-provided category '{requested_category}' "
            f"was received, while the ML classifier predicted "
            f"'{predicted_category}'."
        )

    # --------------------------------------------------------
    # RESPONSE
    #
    # The current TriageResponse schema does not yet expose the
    # category confidence/top-3 fields. Those are available
    # internally in category_result and will be added to the
    # schema in the next API/schema update.
    # --------------------------------------------------------

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return TriageResponse(
        category=category,
        category_confidence=float(
            category_result["confidence"]
        ),
        second_category=category_result["second_category"],
        second_category_confidence=float(
            category_result["second_confidence"]
        ),
        category_margin=float(
            category_result["margin"]
        ),
        category_top_3=category_result["top_3"],
        category_decision=category_result["decision"],
        requires_human_review=(
            category_requires_human_review
        ),
        severity=severity,
        urgency=urgency,
        innovation_required=innovation_required,
        innovation_score=innovation_score,
        routing_type=routing_type,
        routing_confidence=routing_confidence,
        severity_score=severity_score,
        urgency_score=urgency_score,
        routing_reason=routing_reason,
        severity_reason=severity_reason,
        urgency_reason=urgency_reason,
        innovation_reason=innovation_reason,
        model_version=MODEL_VERSION,
    )