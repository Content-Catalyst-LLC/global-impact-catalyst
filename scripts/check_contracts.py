#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.6.0."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "1.6.0"
CONTRACT = "1.1.0"
EVIDENCE = "1.3.0"
REGISTRY = "1.4.0"
MEASUREMENT = "1.5.0"
DATABASE = 7
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
    ("measurement_repository_version", MEASUREMENT), ("review_workflow_version", PACKAGE),
    ("formula_language", "gic-expression-1.0"),
    ("shortcode", "[global_impact_catalyst_demo]"),
    ("workspace_shortcode", "[global_impact_catalyst_workspace]"),
    ("evidence_shortcode", "[global_impact_catalyst_evidence_ledger]"),
    ("indicator_registry_shortcode", "[global_impact_catalyst_indicator_registry]"),
    ("measurement_shortcode", "[global_impact_catalyst_measurement_portfolio]"),
    ("review_workflow_shortcode", "[global_impact_catalyst_review_workflow]"),
):
    require(manifest.get(key) == value, f"manifest {key} mismatch")

path_keys = (
    "core_path", "browser_core_path", "plugin_path", "input_schema_path", "schema_path",
    "compatibility_schema_path", "validation_schema_path", "fixtures_path", "legacy_fixture_path",
    "repository_path", "service_path", "repository_cli_path", "workspace_bundle_schema_path",
    "evidence_chain_schema_path", "evidence_repository_schema_path", "indicator_registry_module_path",
    "indicator_registry_schema_path", "measurement_module_path", "measurement_repository_schema_path",
    "outcome_portfolio_aggregation_schema_path", "beneficiary_summary_schema_path",
    "review_workflow_module_path", "review_workflow_schema_path", "review_workflow_doc_path",
    "review_governance_doc_path", "publication_controls_doc_path", "review_workflow_example_path",
    "database_migration_5", "database_migration_6", "database_migration_7",
)
for key in path_keys:
    value = manifest.get(key)
    require(bool(value), f"manifest key missing: {key}")
    if value:
        require((ROOT / value).exists(), f"manifest path missing: {key} -> {value}")

required_caps = {
    "workflow_roles", "review_assignments", "threaded_review_comments", "comment_resolution",
    "weighted_quality_assessments", "approval_decisions", "approval_gates",
    "immutable_revision_history", "correction_records", "publication_controls",
    "publication_withdrawal", "publication_event_history", "review_workflow_export",
}
require(required_caps.issubset(set(manifest.get("repository_capabilities", []))), "review capabilities incomplete")

repository = read("python/global_impact_repository.py")
for needle in (
    "DATABASE_SCHEMA_VERSION = 7", "ReviewWorkflowMixin", "MeasurementPortfolioMixin", "IndicatorRegistryMixin",
    "007_review_quality_revision_workflow.sql", "self._materialize_contract_workflow",
    '"bundle_version": "1.6.0"', '"review_workflow": self.export_review_workflow(workspace_id)',
    "self._restore_review_workflow", '"workflow_revisions": count("workflow_revisions")',
):
    require(needle in repository, f"repository contract missing: {needle}")

review = read("python/global_impact_review.py")
for needle in (
    'REVIEW_WORKFLOW_VERSION = "1.6.0"', "class WorkflowGateError", "def ensure_default_workflow_roles",
    "def create_review_assignment", "def add_review_comment", "def resolve_review_comment",
    "def submit_quality_assessment", "def record_approval_decision", "def record_workflow_revision",
    "def open_correction", "def apply_contract_correction", "def create_publication", "def publish",
    "def withdraw_publication", "def export_review_workflow", "def _restore_review_workflow",
):
    require(needle in review, f"review workflow contract missing: {needle}")

service = read("python/global_impact_service.py")
for needle in (
    'SERVICE_VERSION = "1.6.0"', "def register_workflow_role", "def create_review_assignment",
    "def add_review_comment", "def submit_quality_assessment", "def record_approval_decision",
    "def open_correction", "def create_publication", "def publish", "def withdraw_publication",
    "def review_workflow",
):
    require(needle in service, f"service contract missing: {needle}")

application = read("app/main.py")
for needle in (
    '"version": "1.6.0"', '"database_schema_version": 7',
    '"measurement_repository_version": "1.5.0"', '"review_workflow_version": "1.6.0"',
):
    require(needle in application, f"application health contract missing: {needle}")

cli = read("scripts/gic_repository.py")
for command in (
    "review-workflow", "add-review-role", "assign-review", "add-review-comment",
    "resolve-review-comment", "assess-quality", "review-decision", "open-correction",
    "create-publication", "publish", "withdraw-publication",
):
    require(f"'{command}'" in cli, f"CLI command missing: {command}")

assets = ROOT / "wordpress/global-impact-catalyst-demo/assets"
for asset in (
    "global-impact-catalyst-demo.js", "global-impact-catalyst-demo.css",
    "global-impact-catalyst-workspace.js", "global-impact-catalyst-workspace.css",
    "global-impact-catalyst-evidence.js", "global-impact-catalyst-evidence.css",
    "global-impact-catalyst-registry.js", "global-impact-catalyst-registry.css",
    "global-impact-catalyst-measurement.js", "global-impact-catalyst-measurement.css",
    "global-impact-catalyst-review.js", "global-impact-catalyst-review.css",
):
    require((assets / asset).exists() and (assets / asset).stat().st_size > 100, f"WordPress asset missing: {asset}")

plugin = read("wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
header = re.search(r"^ \* Version:\s*([^\s]+)", plugin, re.MULTILINE)
constant = re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)", plugin)
require(bool(header) and header.group(1) == PACKAGE, "WordPress plugin header mismatch")
require(bool(constant) and constant.group(1) == PACKAGE, "WordPress plugin constant mismatch")
for needle in (
    "add_shortcode('global_impact_catalyst_review_workflow'", "gic_review_export",
    "gic_review_assignment_rest", "gic_review_comment_rest", "gic_review_quality_rest",
    "gic_review_decision_rest", "gic_review_publication_rest", "gic_review_withdraw_rest",
    "'/review-workflow'", "'/review-assignments'", "'/review-comments'", "'/quality-assessments'",
    "'/approval-decisions'", "'/publications'", "gic_repository_table('review_assignments')",
    "gic_repository_table('workflow_revisions')", "gic_repository_table('publication_records')",
):
    require(needle in plugin, f"WordPress review contract missing: {needle}")

schema_versions = {
    "global_impact_input.schema.json": CONTRACT,
    "global_impact_contract.schema.json": CONTRACT,
    "global_impact_record.schema.json": CONTRACT,
    "global_impact_validation_result.schema.json": CONTRACT,
    "global_impact_evidence_chain.schema.json": EVIDENCE,
    "global_impact_evidence_repository.schema.json": EVIDENCE,
    "global_impact_indicator_registry.schema.json": REGISTRY,
    "global_impact_measurement_repository.schema.json": MEASUREMENT,
    "global_impact_outcome_portfolio_aggregation.schema.json": MEASUREMENT,
    "global_impact_beneficiary_summary.schema.json": MEASUREMENT,
    "global_impact_workspace_bundle.schema.json": PACKAGE,
    "global_impact_review_workflow.schema.json": PACKAGE,
}
for name, version in schema_versions.items():
    schema = load_json("schemas/" + name)
    require(schema.get("x-global-impact-catalyst-version") == version, f"schema version mismatch: {name}")
    require(f"/{version}/" in schema.get("$id", ""), f"schema ID mismatch: {name}")

examples = (
    ("examples/example_global_impact_workspace_bundle.json", "global_impact_workspace_bundle.schema.json"),
    ("examples/example_global_impact_measurement_repository.json", "global_impact_measurement_repository.schema.json"),
    ("examples/example_global_impact_outcome_portfolio_aggregation.json", "global_impact_outcome_portfolio_aggregation.schema.json"),
    ("examples/example_global_impact_review_workflow.json", "global_impact_review_workflow.schema.json"),
)
for example_path, schema_name in examples:
    validator = Draft202012Validator(load_json("schemas/" + schema_name), format_checker=FormatChecker())
    validation_errors = list(validator.iter_errors(load_json(example_path)))
    require(not validation_errors, f"example schema failure: {example_path}: {[e.message for e in validation_errors]}")

migration_names = [p.name for p in sorted((ROOT / "migrations").glob("*.sql"))]
require(migration_names == [
    "001_core_repository.sql", "002_portfolios_and_autosave.sql", "003_imports_audit_and_bundles.sql",
    "004_sources_provenance_evidence.sql", "005_indicator_registry_units_baselines_targets_methods.sql",
    "006_observations_beneficiaries_budgets_outcome_portfolios.sql",
    "007_review_quality_revision_workflow.sql",
], "database migration inventory mismatch")

for path in (
    "docs/review-quality-revision-workflow.md", "docs/review-governance.md",
    "docs/publication-controls.md", "release/v1.6.0.md",
):
    require((ROOT / path).exists() and (ROOT / path).stat().st_size > 300, f"documentation missing: {path}")

changelog = read("CHANGELOG.md")
readme = read("README.md")
require("1.6.0" in changelog and "Review, Quality, and Revision Workflow" in changelog, "CHANGELOG missing v1.6.0")
for needle in (
    "v1.6.0 governance workflow", "[global_impact_catalyst_review_workflow]",
    "immutable revision history", "canonical contract",
):
    require(needle in readme, f"README section missing: {needle}")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)
print("Global Impact Catalyst v1.6.0 release contract passed.")
