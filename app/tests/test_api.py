from app.main import build_demo_response, healthcheck


def test_healthcheck():
    assert healthcheck()["status"] == "ok"


def test_build_demo_response():
    payload = {
        "initiative": "Community Energy Retrofit",
        "goal": "Reduce household energy burden",
        "sdg_theme": "Affordable and clean energy",
        "indicator": "Average monthly bill reduction",
        "unit": "USD",
        "baseline_value": 0,
        "current_value": 18,
        "target_value": 30,
        "baseline_period": "2025",
        "current_period": "2026 Q2",
        "source": "Pilot utility billing sample",
        "method_notes": "Difference between baseline average bill and post-retrofit monthly bill sample.",
    }
    result = build_demo_response(payload)
    assert result["record_type"] == "global_impact_catalyst_record"
    assert result["metrics"]["progress_to_target_percent"] == 60.0
