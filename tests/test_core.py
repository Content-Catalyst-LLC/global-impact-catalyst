from __future__ import annotations

import pytest

from python.global_impact_core import InputValidationError, build_impact_record, input_from_dict, record_to_dict

BASE = {
    "initiative": "Test initiative",
    "goal": "Test goal",
    "sdg_theme": "Climate action",
    "indicator": "Indicator",
    "unit": "units",
    "baseline_value": 10,
    "current_value": 15,
    "target_value": 20,
    "baseline_period": "2025",
    "current_period": "2026",
    "source": "A documented source",
    "method_notes": "A sufficiently detailed method description.",
}


def record(**overrides):
    data = {**BASE, **overrides}
    return record_to_dict(build_impact_record(input_from_dict(data), generated_at="2026-07-17T16:00:00+00:00"))


def test_higher_is_better_progress():
    assert record()["metrics"]["progress_to_target_percent"] == 50.0


def test_lower_is_better_and_false_string():
    result = record(baseline_value=100, current_value=70, target_value=50, higher_is_better="false")
    assert result["higher_is_better"] is False
    assert result["metrics"]["progress_to_target_percent"] == 60.0
    assert result["metrics"]["remaining_gap"] == 20.0


def test_zero_baseline_has_null_percent_change():
    result = record(baseline_value=0, current_value=5, target_value=10)
    assert result["metrics"]["percent_change_from_baseline"] is None
    assert result["metrics"]["progress_to_target_percent"] == 50.0


def test_equal_baseline_and_target_requires_review():
    result = record(baseline_value=10, current_value=10, target_value=10)
    assert result["metrics"]["progress_to_target_percent"] is None
    assert result["metrics"]["status"] == "needs baseline/target review"


def test_progress_below_zero_and_above_100():
    assert record(current_value=5)["metrics"]["progress_to_target_percent"] == -50.0
    assert record(current_value=25)["metrics"]["progress_to_target_percent"] == 150.0


def test_negative_decimal_values():
    result = record(baseline_value=-10.5, current_value=-5.25, target_value=0)
    assert result["metrics"]["absolute_change"] == 5.25
    assert result["metrics"]["progress_to_target_percent"] == 50.0


def test_blank_source_and_method_reduce_signal():
    result = record(source="", method_notes="")
    components = result["metrics"]["data_quality_components"]
    assert components["source_documented"] == 0
    assert components["method_documented"] == 0


def test_invalid_enums_use_canonical_defaults():
    result = record(confidence="certain", review_status="approved")
    assert result["confidence"] == "medium"
    assert result["review_status"] == "draft"


def test_zero_and_absent_optional_fields_are_distinct():
    explicit = record(beneficiaries=0, budget_usd=0)
    absent = record(beneficiaries=None, budget_usd=None)
    assert explicit["beneficiaries"] == 0 and explicit["budget_usd"] == 0
    assert absent["beneficiaries"] is None and absent["budget_usd"] is None
    assert explicit["metrics"]["cost_per_beneficiary_usd"] is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("baseline_value", "not-a-number"),
        ("current_value", float("inf")),
        ("target_value", True),
        ("higher_is_better", "maybe"),
        ("beneficiaries", 1.5),
        ("beneficiaries", -1),
        ("budget_usd", -0.01),
    ],
)
def test_malformed_inputs_raise(field, value):
    with pytest.raises(InputValidationError):
        input_from_dict({**BASE, field: value})
