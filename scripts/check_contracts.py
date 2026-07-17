#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.8.0."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "1.8.0"
CONTRACT = "1.1.0"
EVIDENCE = "1.3.0"
REGISTRY = "1.4.0"
MEASUREMENT = "1.5.0"
REVIEW = "1.6.0"
ANALYSIS = "1.7.0"
REPORTING = "1.8.0"
DATABASE = 9
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str):
    return json.loads(read(path))


manifest = load("global_impact_catalyst_manifest.json")
expected_manifest = {
    "version": PACKAGE,
    "contract_version": CONTRACT,
    "schema_version": CONTRACT,
    "database_schema_version": DATABASE,
    "workspace_bundle_version": PACKAGE,
    "evidence_chain_version": EVIDENCE,
    "indicator_registry_version": REGISTRY,
    "measurement_repository_version": MEASUREMENT,
    "review_workflow_version": REVIEW,
    "analysis_repository_version": ANALYSIS,
    "reporting_repository_version": REPORTING,
    "reporting_shortcode": "[global_impact_catalyst_reporting_studio]",
}
for key, expected in expected_manifest.items():
    require(manifest.get(key) == expected, f"manifest {key} mismatch: {manifest.get(key)!r}")

path_keys = [
    "core_path", "repository_path", "service_path", "repository_cli_path",
    "workspace_bundle_schema_path", "reporting_module_path",
    "reporting_repository_schema_path", "reproducible_export_schema_path",
    "reporting_doc_path", "reproducible_exports_doc_path",
    "accessible_reporting_doc_path", "reporting_repository_example_path",
    "reproducible_export_example_path", "database_migration_9",
]
for key in path_keys:
    value = manifest.get(key)
    require(bool(value) and (ROOT / value).exists(), f"manifest path missing: {key} -> {value}")

required_capabilities = {
    "report_template_registry", "accessible_html_reports", "markdown_reports",
    "structured_citations", "methodology_appendices", "dashboard_definitions",
    "accessible_dashboard_cards", "publication_snapshots",
    "cross_repository_snapshot_hashes", "deterministic_zip_exports",
    "fixed_archive_timestamps", "artifact_manifests", "sha256_artifact_checksums",
    "export_verification", "reporting_repository_export",
    "lossless_reporting_restore", "wordpress_reporting_studio",
}
require(required_capabilities.issubset(set(manifest.get("repository_capabilities", []))),
        "reporting capabilities incomplete")

repository = read("python/global_impact_repository.py")
for marker in [
    "DATABASE_SCHEMA_VERSION = 9", "ReportingPublicationMixin",
    "009_reporting_publication_reproducible_exports.sql",
    '"bundle_version": "1.8.0"',
    '"reporting_repository": self.export_reporting_repository(workspace_id)',
    "self._restore_reporting_repository",
    '"report_documents": count("report_documents")',
    '"export_bundles": count("export_bundles")',
]:
    require(marker in repository, f"repository contract missing: {marker}")

reporting = read("python/global_impact_reporting.py")
for marker in [
    'REPORTING_VERSION = "1.8.0"', "def register_report_template",
    "def create_report", "def create_dashboard", "def add_dashboard_card",
    "def create_publication_snapshot", "def build_reproducible_export",
    "def verify_reproducible_export", "def export_reporting_repository",
    "def _restore_reporting_repository", "deterministic_zip_timestamps",
    "artifact_checksum_failures", "bundle_archive_failures",
]:
    require(marker in reporting, f"reporting contract missing: {marker}")

service = read("python/global_impact_service.py")
for marker in [
    'SERVICE_VERSION = "1.8.0"', "def register_report_template",
    "def create_report", "def create_dashboard", "def create_publication_snapshot",
    "def build_reproducible_export", "def reporting_repository",
]:
    require(marker in service, f"service contract missing: {marker}")

app = read("app/main.py")
for marker in [
    '"version": "1.8.0"', '"database_schema_version": 9',
    '"analysis_repository_version": "1.7.0"',
    '"reporting_repository_version": "1.8.0"',
]:
    require(marker in app, f"application contract missing: {marker}")

cli = read("scripts/gic_repository.py")
for command in [
    "add-report-template", "create-report", "reports", "add-dashboard",
    "add-dashboard-card", "render-dashboard", "publication-snapshot",
    "reproducible-export", "verify-export", "reporting-repository",
]:
    require(f"'{command}'" in cli, f"CLI command missing: {command}")

assets = ROOT / "wordpress/global-impact-catalyst-demo/assets"
js_assets = [
    "global-impact-catalyst-demo.js", "global-impact-catalyst-workspace.js",
    "global-impact-catalyst-evidence.js", "global-impact-catalyst-registry.js",
    "global-impact-catalyst-measurement.js", "global-impact-catalyst-review.js",
    "global-impact-catalyst-analysis.js", "global-impact-catalyst-reporting.js",
]
for asset in js_assets + ["global-impact-catalyst-reporting.css"]:
    path = assets / asset
    require(path.exists() and path.stat().st_size > 100, f"WordPress asset missing: {asset}")

plugin = read("wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
header = re.search(r"^ \* Version:\s*([^\s]+)", plugin, re.M)
constant = re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)", plugin)
require(bool(header) and header.group(1) == PACKAGE, "WordPress header mismatch")
require(bool(constant) and constant.group(1) == PACKAGE, "WordPress constant mismatch")
for marker in [
    "add_shortcode('global_impact_catalyst_reporting_studio'", "/reporting-repository",
    "/report-templates", "/reports", "/dashboards", "/publication-snapshots",
    "/reproducible-exports", "gic_reporting_snapshot_rest",
    "gic_reporting_export_rest", "gic_repository_table('report_templates')",
    "gic_repository_table('publication_snapshots')", "gic_repository_table('export_artifacts')",
]:
    require(marker in plugin, f"WordPress reporting contract missing: {marker}")

schema_versions = {
    "global_impact_input.schema.json": CONTRACT,
    "global_impact_contract.schema.json": CONTRACT,
    "global_impact_record.schema.json": CONTRACT,
    "global_impact_validation_result.schema.json": CONTRACT,
    "global_impact_evidence_chain.schema.json": EVIDENCE,
    "global_impact_evidence_repository.schema.json": EVIDENCE,
    "global_impact_indicator_registry.schema.json": REGISTRY,
    "global_impact_measurement_repository.schema.json": MEASUREMENT,
    "global_impact_review_workflow.schema.json": REVIEW,
    "global_impact_analysis_repository.schema.json": ANALYSIS,
    "global_impact_reporting_repository.schema.json": REPORTING,
    "global_impact_reproducible_export.schema.json": REPORTING,
    "global_impact_workspace_bundle.schema.json": PACKAGE,
}
for filename, version in schema_versions.items():
    schema = load("schemas/" + filename)
    require(schema.get("x-global-impact-catalyst-version") == version,
            f"schema version mismatch: {filename}")
    require(f"/{version}/" in schema.get("$id", ""), f"schema id mismatch: {filename}")

examples = [
    ("examples/example_global_impact_reporting_repository.json", "global_impact_reporting_repository.schema.json"),
    ("examples/example_global_impact_reproducible_export_manifest.json", "global_impact_reproducible_export.schema.json"),
    ("examples/example_global_impact_workspace_bundle.json", "global_impact_workspace_bundle.schema.json"),
    ("examples/example_global_impact_analysis_repository.json", "global_impact_analysis_repository.schema.json"),
    ("examples/example_global_impact_review_workflow.json", "global_impact_review_workflow.schema.json"),
]
for example, schema_name in examples:
    validator = Draft202012Validator(load("schemas/" + schema_name), format_checker=FormatChecker())
    failures = sorted(validator.iter_errors(load(example)), key=lambda e: list(e.path))
    require(not failures, f"example schema failure: {example}: {[e.message for e in failures[:5]]}")

expected_migrations = [
    "001_core_repository.sql", "002_portfolios_and_autosave.sql",
    "003_imports_audit_and_bundles.sql", "004_sources_provenance_evidence.sql",
    "005_indicator_registry_units_baselines_targets_methods.sql",
    "006_observations_beneficiaries_budgets_outcome_portfolios.sql",
    "007_review_quality_revision_workflow.sql",
    "008_trends_comparisons_scenarios_uncertainty.sql",
    "009_reporting_publication_reproducible_exports.sql",
]
actual_migrations = [path.name for path in sorted((ROOT / "migrations").glob("*.sql"))]
require(actual_migrations == expected_migrations, "database migration inventory mismatch")

for path in [
    "docs/reporting-publication-export-studio.md", "docs/reproducible-exports.md",
    "docs/accessible-reporting.md", "docs/database-migrations.md",
    "docs/workspace-bundles.md", "release/v1.8.0.md",
]:
    file = ROOT / path
    require(file.exists() and file.stat().st_size > 300, f"documentation missing: {path}")

require("1.8.0" in read("CHANGELOG.md") and
        "Reporting, Publication, and Reproducible Export Studio" in read("CHANGELOG.md"),
        "changelog entry missing")
require("[global_impact_catalyst_reporting_studio]" in read("README.md"),
        "README reporting shortcode missing")
require("eight shortcodes" in read("wordpress/global-impact-catalyst-demo/README.md"),
        "WordPress README release identity missing")

fixture_count = len(list((ROOT / "contracts/fixtures").glob("*.json")))
require(fixture_count == 15, f"expected 15 canonical browser fixtures, found {fixture_count}")

if errors:
    print("Global Impact Catalyst v1.8.0 release contract failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print("Global Impact Catalyst v1.8.0 release contract passed.")
