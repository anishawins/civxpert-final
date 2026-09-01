def test_analysis_result_contract(monkeypatch):
    import app

    monkeypatch.setattr(app, "route_complaint", lambda text: ("Public Works Department", "Roads"))
    monkeypatch.setattr(app, "predict_priority", lambda text: ("High", 91.5))

    result = app.analyze("Large pothole creating a traffic hazard")

    assert result == {
        "department": "Public Works Department",
        "category": "Roads",
        "priority": "High",
        "confidence": 91.5,
    }
