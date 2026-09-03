from services.priority_queue import build_triage_decision


def test_high_priority_produces_immediate_review_action():
    decision = build_triage_decision("High", 90.0)
    assert decision.priority == "High"
    assert decision.urgency_score > 0.7
    assert "immediate" in decision.action.lower()


def test_duplicate_context_is_bounded():
    low = build_triage_decision("Low", 80.0, similar_count=0)
    many = build_triage_decision("Low", 80.0, similar_count=100)
    assert many.urgency_score <= 1.0
    assert many.urgency_score > low.urgency_score
