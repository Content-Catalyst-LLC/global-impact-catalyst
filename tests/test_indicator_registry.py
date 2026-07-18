from __future__ import annotations
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_registry import FormulaValidationError, UnitCompatibilityError, evaluate_formula_expression
from python.global_impact_repository import OptimisticConcurrencyError, SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService

ROOT = Path(__file__).resolve().parents[1]
FIXED = "2026-07-17T18:00:00+00:00"


def payload():
    return json.loads((ROOT / "data/sample_global_impact_input.json").read_text())


def create(repo):
    return ImpactApplicationService(repo).create_initiative(payload(), generated_at=FIXED)


def test_migration_seeds_governed_standard_units(tmp_path):
    with SQLiteImpactRepository(tmp_path / "units.sqlite3") as repo:
        assert repo.schema_version == 12
        assert len(repo.list_units()) >= 18
        assert repo.get_unit("USD")["unit_id"] == "gic-unit-usd"
        assert repo.get_unit("tCO2e")["dimension"] == "emissions"


def test_unit_conversion_requires_compatible_dimensions(tmp_path):
    with SQLiteImpactRepository(tmp_path / "convert.sqlite3") as repo:
        assert repo.convert_value(2, "MWh", "kWh") == 2000.0
        assert repo.convert_value(1.5, "tCO2e", "kgCO2e") == 1500.0
        assert repo.convert_value(25, "%", "ratio") == 0.25
        with pytest.raises(UnitCompatibilityError):
            repo.convert_value(1, "kg", "kWh")


def test_custom_unit_revision_control_and_workspace_precedence(tmp_path):
    with SQLiteImpactRepository(tmp_path / "custom-unit.sqlite3") as repo:
        unit = repo.register_unit({"code": "person-day", "name": "Person day", "dimension": "labor"}, workspace_id="ws-1")
        updated = repo.register_unit({**unit, "name": "Person-day", "metadata": unit["metadata"]}, workspace_id="ws-1", expected_revision=1)
        assert updated["revision"] == 2
        assert repo.get_unit("person-day", workspace_id="ws-1")["name"] == "Person-day"
        with pytest.raises(OptimisticConcurrencyError):
            repo.register_unit({"unit_id": unit["unit_id"], "code": "person-day", "name": "Stale", "dimension": "labor"}, workspace_id="ws-1", expected_revision=1)


def test_indicator_definition_versions_are_immutable_and_deduplicated(tmp_path):
    with SQLiteImpactRepository(tmp_path / "indicator.sqlite3") as repo:
        first = repo.register_indicator_definition({"name": "Energy saved", "description": "Measured energy avoided.", "unit": "kWh", "direction": "higher_is_better", "aggregation_method": "sum", "version_label": "1.0"}, workspace_id="ws")
        repeated = repo.register_indicator_definition({"indicator_definition_id": first["indicator_definition_id"], "name": "Energy saved", "description": "Measured energy avoided.", "unit": "kWh", "direction": "higher_is_better", "aggregation_method": "sum", "version_label": "1.0"}, workspace_id="ws", expected_revision=1)
        changed = repo.register_indicator_definition({"indicator_definition_id": first["indicator_definition_id"], "name": "Energy saved", "description": "Metered energy avoided after approved normalization.", "unit": "kWh", "direction": "higher_is_better", "aggregation_method": "sum", "version_label": "1.1"}, workspace_id="ws", expected_revision=2)
        assert repeated["current_version"] == 1
        assert len(repeated["versions"]) == 1
        assert changed["current_version"] == 2
        assert len(changed["versions"]) == 2
        assert changed["versions"][0]["definition_hash"] != changed["versions"][1]["definition_hash"]


def test_safe_formula_language_accepts_arithmetic_and_rejects_calls():
    assert evaluate_formula_expression("baseline + (current - baseline) / 2", {"baseline": 10, "current": 30}) == 20
    with pytest.raises(FormulaValidationError):
        evaluate_formula_expression("__import__('os').system('true')", {"baseline": 1})
    with pytest.raises(FormulaValidationError):
        evaluate_formula_expression("unknown + 1", {"baseline": 1})


def test_baseline_models_compute_point_average_rolling_benchmark_and_formula(tmp_path):
    with SQLiteImpactRepository(tmp_path / "baseline.sqlite3") as repo:
        average = repo.register_baseline_model({"name": "Three-period average", "method_type": "period_average", "unit": "kWh", "minimum_observations": 3}, workspace_id="ws")
        rolling = repo.register_baseline_model({"name": "Rolling two", "method_type": "rolling_average", "rolling_periods": 2, "unit": "kWh"}, workspace_id="ws")
        benchmark = repo.register_baseline_model({"name": "Sector benchmark", "method_type": "benchmark", "benchmark_value": 125, "unit": "kWh"}, workspace_id="ws")
        modelled = repo.register_baseline_model({"name": "Adjusted average", "method_type": "modelled", "formula_expression": "mean_value * 0.9", "unit": "kWh"}, workspace_id="ws")
        assert repo.compute_baseline(average["baseline_model_id"], [100, 120, 140])["value"] == 120
        assert repo.compute_baseline(rolling["baseline_model_id"], [100, 120, 160])["value"] == 140
        assert repo.compute_baseline(benchmark["baseline_model_id"], [1])["value"] == 125
        assert repo.compute_baseline(modelled["baseline_model_id"], [100, 120])["value"] == 99


def test_target_models_evaluate_absolute_relative_range_and_trajectory(tmp_path):
    with SQLiteImpactRepository(tmp_path / "targets.sqlite3") as repo:
        absolute = repo.register_target_model({"name": "Absolute target", "target_type": "absolute", "target_value": 30, "unit": "USD"}, workspace_id="ws")
        relative = repo.register_target_model({"name": "Relative target", "target_type": "relative_change", "relative_change_percent": 20, "unit": "USD"}, workspace_id="ws")
        range_model = repo.register_target_model({"name": "Target range", "target_type": "range", "lower_value": 25, "upper_value": 35, "unit": "USD"}, workspace_id="ws")
        trajectory = repo.register_target_model({"name": "Linear path", "target_type": "trajectory", "start_value": 10, "end_value": 30, "trajectory_type": "linear", "unit": "USD"}, workspace_id="ws")
        assert repo.evaluate_target(absolute["target_model_id"])["value"] == 30
        assert repo.evaluate_target(relative["target_model_id"], baseline_value=100)["value"] == 120
        assert repo.evaluate_target(range_model["target_model_id"])["lower_value"] == 25
        assert repo.evaluate_target(trajectory["target_model_id"], progress_fraction=0.5)["value"] == 20


def test_method_registry_captures_quality_inputs_limitations_and_versions(tmp_path):
    with SQLiteImpactRepository(tmp_path / "methods.sqlite3") as repo:
        method = repo.register_method_definition({"name": "Weather-normalized billing comparison", "method_kind": "measurement", "design_type": "before_after", "description": "Compares billing periods after weather normalization.", "input_requirements": ["monthly bills", "heating degree days"], "quality_profile": {"reproducibility": "documented", "data_quality": "reviewed"}, "limitations": ["occupancy changes may remain"]}, workspace_id="ws")
        assert method["current_version"] == 1
        assert method["input_requirements"] == ["monthly bills", "heating degree days"]
        assert method["limitations"] == ["occupancy changes may remain"]
        assert method["versions"][0]["method"]["design_type"] == "before_after"


def test_contract_save_materializes_complete_indicator_registry_binding(tmp_path):
    with SQLiteImpactRepository(tmp_path / "materialize.sqlite3") as repo:
        created = create(repo)
        registry = repo.export_indicator_registry(created["repository"]["workspace_id"])
        assert registry["integrity"]["valid"] is True
        assert registry["integrity"]["indicator_definition_count"] == 1
        assert registry["integrity"]["baseline_model_count"] == 1
        assert registry["integrity"]["target_model_count"] == 1
        assert registry["integrity"]["method_definition_count"] == 1
        assert registry["integrity"]["binding_count"] == 1
        binding = registry["bindings"][0]
        assert binding["indicator_id"] == created["contract"]["facts"]["indicator"]["id"]
        assert binding["unit_id"] == "gic-unit-usd"


def test_binding_rejects_incompatible_baseline_or_target_units(tmp_path):
    with SQLiteImpactRepository(tmp_path / "binding.sqlite3") as repo:
        indicator = repo.register_indicator_definition({"name": "Energy saved", "unit": "kWh"}, workspace_id="ws")
        baseline = repo.register_baseline_model({"name": "Mass baseline", "method_type": "benchmark", "benchmark_value": 1, "unit": "kg"}, workspace_id="ws")
        with pytest.raises(UnitCompatibilityError):
            repo.bind_indicator_registry(workspace_id="ws", initiative_id="i", indicator_id="indicator", indicator_definition_id=indicator["indicator_definition_id"], baseline_model_id=baseline["baseline_model_id"])


def test_registry_export_and_workspace_restore_are_lossless_and_idempotent(tmp_path):
    with SQLiteImpactRepository(tmp_path / "source.sqlite3") as source:
        created = create(source)
        workspace_id = created["repository"]["workspace_id"]
        initiative_id = created["repository"]["initiative_id"]
        registry = source.export_indicator_registry(workspace_id)
        bundle = source.export_workspace_bundle(workspace_id)
        assert bundle["bundle_version"] == "2.0.0"
        assert bundle["indicator_registry"]["integrity"]["valid"] is True
    original = copy.deepcopy(bundle)
    with SQLiteImpactRepository(tmp_path / "target.sqlite3") as target:
        result = target.restore_workspace_bundle(bundle)
        assert result["status"] == "restored"
        restored = target.export_indicator_registry(workspace_id)
        assert restored["integrity"] == registry["integrity"]
        assert target.get_contract(initiative_id=initiative_id)["contract"]["derived"]["metrics"] == created["contract"]["derived"]["metrics"]
        assert target.restore_workspace_bundle(original)["status"] == "unchanged"


def test_indicator_registry_export_validates_against_schema(tmp_path):
    with SQLiteImpactRepository(tmp_path / "schema.sqlite3") as repo:
        created = create(repo)
        registry = repo.export_indicator_registry(created["repository"]["workspace_id"])
    schema = json.loads((ROOT / "schemas/global_impact_indicator_registry.schema.json").read_text())
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(registry))
    assert not errors, [error.message for error in errors]
