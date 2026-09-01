from types import SimpleNamespace

from services.duplicate_detector import ComplaintSimilarity


def test_similar_complaints_are_ranked():
    detector = ComplaintSimilarity(threshold=0.2)
    complaints = [
        SimpleNamespace(id=1, text="Water pipe leaking near the school"),
        SimpleNamespace(id=2, text="Street light is broken"),
    ]
    matches = detector.find_similar("There is a leaking water pipe by the school", complaints)
    assert matches
    assert matches[0]["complaint"].id == 1
    assert matches[0]["score"] > matches[1]["score"] if len(matches) > 1 else True


def test_empty_input_returns_no_matches():
    detector = ComplaintSimilarity()
    assert detector.find_similar("", []) == []
