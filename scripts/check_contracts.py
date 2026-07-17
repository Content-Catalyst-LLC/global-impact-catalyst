#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.5.0."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "1.5.0"
CONTRACT = "1.1.0"
EVIDENCE = "1.3.0"
REGISTRY = "1.4.0"
DATABASE = 6
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str):
    return json.loads(read(path))


manifest = load_json("global_impact_catalyst_manifest.json")
for key, value in (
    ("version", PACKAGE), ("contract_version", CONTRACT), ("schema_version", CONTRACT),
    ("database_schema_version", DATABASE), ("workspace_bundle_version", PACKAGE),
    ("evidence_chain_version", EVIDENCE), ("indicator_registry_version", REGISTRY),
    ("measurement_repository_version", PACKAGE), ("formula_language", "gic-expression-1.0"),
    ("shortcode", "[global_impact_catalyst_demo]"),
    ("workspace_shortcode", "[global_impact_catalyst_workspace]"),
    ("evidence_shortcode", "[global_impact_catalyst_evidence_ledger]"),
    ("indicator_registry_shortcode", "[global_impact_catalyst_indicator_registry]"),
    ("measurement_shortcode", "[global_impact_catalyst_measurement_portfolio]"),
):
    require(manifest.get(key) == value, f"manifest {key} mismatch")

path_keys = (
    "core_path", "browser_core_path", "plugin_path", "input_schema_path", "schema_path",
    "compatibility_schema_path", "validation_schema_path", "fixtures_path", "legacy_fixture_path",
    "repository_path", "service_path", "repository_cli_path", "workspace_bundle_schema_path",
    "evidence_chain_schema_path", "evidence_repository_schema_path", "indicator_registry_module_path",
    "indicator_registry_schema_path", "measurement_module_path", "measurement_repository_schema_path",
    "outcome_portfolio_aggregation_schema_path", "beneficiary_summary_schema_path",
    "program_measurement_doc_path", "beneficiary_governance_doc_path", "budget_cost_metrics_doc_path",
    "outcome_portfolio_doc_path", "measurement_repository_example_path", "outcome_portfolio_example_path",
    "database_migration_5", "database_migration_6",
)
for key in path_keys:
    value = manifest.get(key)
    require(bool(value), f"manifest key missing: {key}")
    if value:
        require((ROOT / value).exists(), f"manifest path missing: {key} -> {value}")

required_caps = {
    "multi_period_observations", "observation_revisions", "observation_data_states",
    "aggregate_disaggregation", "beneficiary_definitions", "direct_indirect_reach",
    "privacy_safe_beneficiary_aggregation", "beneficiary_overlap_disclosure",
    "budgets_and_expenditures", "explicit_exchange_rates", "cost_per_output",
    "cost_per_outcome", "cost_per_beneficiary", "output_outcome_impact_relationships",
    "external_factors", "contribution_notes", "outcome_portfolios", "aggregation_guards",
    "period_compatibility", "population_overlap_guards", "measurement_repository_export",
}
require(required_caps.issubset(set(manifest.get("repository_capabilities", []))), "measurement capabilities incomplete")

repository = read("python/global_impact_repository.py")
for needle in (
    "DATABASE_SCHEMA_VERSION = 6", "MeasurementPortfolioMixin", "IndicatorRegistryMixin",
    "006_observations_beneficiaries_budgets_outcome_portfolios.sql",
    "self._materialize_contract_measurement", '"bundle_version": "1.5.0"',
    '"measurement_repository": self.export_measurement_repository(workspace_id)',
    "self._restore_measurement_repository", '"observation_series": count("observation_series")',
):
    require(needle in repository, f"repository contract missing: {needle}")

measurement = read("python/global_impact_measurement.py")
for needle in (
    'MEASUREMENT_REPOSITORY_VERSION = "1.5.0"', "class PrivacyBoundaryError",
    "class AggregationGuardError", "def record_observation", "def observation_time_series",
    "def register_beneficiary_definition", "def beneficiary_summary", "def record_financial_record",
    "def calculate_cost_metric", "def register_impact_result", "def relate_impact_results",
    "def add_external_factor", "def add_contribution_note", "def create_outcome_portfolio",
    "def aggregate_outcome_portfolio", "def export_measurement_repository",
    "def _restore_measurement_repository",
):
    require(needle in measurement, f"measurement contract missing: {needle}")

service = read("python/global_impact_service.py")
for needle in (
    'SERVICE_VERSION = "1.5.0"', "def record_observation", "def observation_series",
    "def register_beneficiary_definition", "def record_beneficiary_observation",
    "def record_financial_record", "def create_outcome_portfolio",
    "def aggregate_outcome_portfolio", "def measurement_repository",
):
    require(needle in service, f"service contract missing: {needle}")

application = read("app/main.py")
for needle in (
    '"version": "1.5.0"', '"database_schema_version": 6',
    '"indicator_registry_version": "1.4.0"', '"measurement_repository_version": "1.5.0"',
):
    require(needle in application, f"application health contract missing: {needle}")

cli = read("scripts/gic_repository.py")
for command in (
    "add-impact-result", "add-observation", "observation-series", "add-beneficiary-definition",
    "add-beneficiary-observation", "beneficiary-summary", "add-financial-record", "financial-summary",
    "cost-metric", "add-external-factor", "add-contribution-note", "add-outcome-portfolio",
    "add-outcome-member", "aggregate-outcome-portfolio", "measurement-repository",
):
    require(f"'{command}'" in cli, f"CLI command missing: {command}")

assets = ROOT / "wordpress/global-impact-catalyst-demo/assets"
for asset in (
    "global-impact-catalyst-demo.js", "global-impact-catalyst-demo.css",
    "global-impact-catalyst-workspace.js", "global-impact-catalyst-workspace.css",
    "global-impact-catalyst-evidence.js", "global-impact-catalyst-evidence.css",
    "global-impact-catalyst-registry.js", "global-impact-catalyst-registry.css",
    "global-impact-catalyst-measurement.js", "global-impact-catalyst-measurement.css",
):
    require((assets / asset).exists() and (assets / asset).stat().st_size > 100, f"WordPress asset missing: {asset}")

plugin = read("wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
header = re.search(r"^ \* Version:\s*([^\s]+)", plugin, re.MULTILINE)
constant = re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)", plugin)
require(bool(header) and header.group(1) == PACKAGE, "WordPress plugin header mismatch")
require(bool(constant) and constant.group(1) == PACKAGE, "WordPress plugin constant mismatch")
for needle in (
    "add_shortcode('global_impact_catalyst_measurement_portfolio'", "gic_measurement_repository_export",
    "gic_measurement_observation_rest", "gic_measurement_beneficiary_definition_rest",
    "gic_measurement_financial_rest", "gic_measurement_portfolio_aggregate_rest",
    "'/measurement-repository'", "'/observations'", "'/beneficiary-definitions'",
    "'/beneficiary-observations'", "'/financial-records'", "'/outcome-portfolios'",
    "gic_repository_table('observation_series')", "gic_repository_table('beneficiary_definitions')",
    "gic_repository_table('outcome_portfolios')",
):
    require(needle in plugin, f"WordPress measurement contract missing: {needle}")

schema_versions = {
    "global_impact_input.schema.json": CONTRACT,
    "global_impact_contract.schema.json": CONTRACT,
    "global_impact_record.schema.json": CONTRACT,
    "global_impact_validation_result.schema.json": CONTRACT,
    "global_impact_evidence_chain.schema.json": EVIDENCE,
    "global_impact_evidence_repository.schema.json": EVIDENCE,
    "global_impact_indicator_registry.schema.json": REGISTRY,
    "global_impact_workspace_bundle.schema.json": PACKAGE,
    "global_impact_measurement_repository.schema.json": PACKAGE,
    "global_impact_outcome_portfolio_aggregation.schema.json": PACKAGE,
    "global_impact_beneficiary_summary.schema.json": PACKAGE,
}
for name, version in schema_versions.items():
    schema = load_json("schemas/" + name)
    require(schema.get("x-global-impact-catalyst-version") == version, f"schema version mismatch: {name}")
    require(f"/{version}/" in schema.get("$id", ""), f"schema ID mismatch: {name}")

examples = (
    ("examples/example_global_impact_workspace_bundle.json", "global_impact_workspace_bundle.schema.json"),
    ("examples/example_global_impact_measurement_repository.json", "global_impact_measurement_repository.schema.json"),
    ("examples/example_global_impact_outcome_portfolio_aggregation.json", "global_impact_outcome_portfolio_aggregation.schema.json"),
)
for example_path, schema_name in examples:
    validator = Draft202012Validator(load_json("schemas/" + schema_name), format_checker=FormatChecker())
    validation_errors = list(validator.iter_errors(load_json(example_path)))
    require(not validation_errors, f"example schema failure: {example_path}: {[e.message for e in validation_errors]}")

fixtures = sorted((ROOT / "contracts/fixtures").glob("*.json"))
require(len(fixtures) >= 15, "canonical fixture suite must contain at least 15 fixtures")
for path in fixtures:
    require(load_json(str(path.relative_to(ROOT))).get("expected", {}).get("contract_version") == CONTRACT, f"fixture mismatch: {path.name}")

migration_names = [p.name for p in sorted((ROOT / "migrations").glob("*.sql"))]
require(migration_names == [
    "001_core_repository.sql", "002_portfolios_and_autosave.sql", "003_imports_audit_and_bundles.sql",
    "004_sources_provenance_evidence.sql", "005_indicator_registry_units_baselines_targets_methods.sql",
    "006_observations_beneficiaries_budgets_outcome_portfolios.sql",
], "database migration inventory mismatch")

for path in (
    "docs/program-measurement.md", "docs/beneficiary-governance.md", "docs/budgets-and-cost-metrics.md",
    "docs/outcome-portfolios.md", "release/v1.5.0.md",
):
    require((ROOT / path).exists() and (ROOT / path).stat().st_size > 300, f"documentation missing: {path}")

changelog = read("CHANGELOG.md")
readme = read("README.md")
require("## [1.5.0]" in changelog, "CHANGELOG missing v1.5.0")
for needle in (
    "Observations, Beneficiaries, Budgets, and Outcome Portfolios",
    "[global_impact_catalyst_measurement_portfolio]", "aggregate beneficiary",
    "canonical calculation contract remains v1.1.0",
):
    require(needle in readme, f"README section missing: {needle}")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)
print("Global Impact Catalyst v1.5.0 release contract passed.")
