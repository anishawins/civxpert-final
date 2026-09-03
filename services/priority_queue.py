"""Deterministic operational scoring built on top of model predictions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TriageDecision:
    priority: str
    confidence: float
    urgency_score: float
    action: str


def build_triage_decision(priority: str, confidence: float, similar_count: int = 0) -> TriageDecision:
    """Translate model output into an explainable operational queue signal.

    This does not alter the ML prediction. The urgency score is a separate
    business metric that combines model confidence with duplicate context.
    """
    base = {"High": 1.0, "Medium": 0.6, "Low": 0.25}.get(priority, 0.25)
    duplicate_boost = min(similar_count * 0.03, 0.15)
    urgency = round(min(1.0, base * (0.5 + confidence / 200.0) + duplicate_boost), 3)
    action = {
        "High": "Prioritize immediate review",
        "Medium": "Review within normal service queue",
        "Low": "Handle in standard queue",
    }.get(priority, "Review manually")
    return TriageDecision(priority, confidence, urgency, action)
