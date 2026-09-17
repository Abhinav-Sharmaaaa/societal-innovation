"""
Model loading abstraction.

The first implementation uses the rule-based triage engine.
Later this module can load the trained ML model produced from
the 50K+ societal challenge dataset.
"""

from app.ai.triage_service import MODEL_VERSION


def get_model_version() -> str:
    return MODEL_VERSION