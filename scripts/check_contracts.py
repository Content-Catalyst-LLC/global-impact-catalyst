#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v2.0.0."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "2.0.0"
CONTRACT = "1.1.0"
DATABASE = 12
VERSIONS = {
    "evidence_chain_version": "1.3.0",
    "indicator_registry_version": "1.4.0",
    "measurement_repository_version": "1.5.0",
    "review_workflow_version": "1.6.0",
    "analysis_repository_version": "1.7.0",
    "reporting_repository_version": "1.8.0",
    "integration_repository_version": "1.9.0",
    "production_repository_version": "1.10.0",
    "platform_repository_version": "2.0.0",
}
errors: list[str] = []


def require(ok: bool, message: str) -> None:
    if not ok:
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
    "api_version": "v1",
    **VERSIONS,
}
for key, expected in expected_manifest.items():
    require(manifest.get(key) == expected, f"manifest {key} mismatch: {manifest.get(key)!r}")

for key in [
    "core_path", "repository_path", "service_path", "repository_cli_path", "workspace_bundle_schema_path",
    "platform_module_path", "platform_repository_schema_path", "platform_repository_example_path",
    "platform_doc_path", "database_migration_12",
]:
    value = manifest.get(key)
    require(bool(value) and (ROOT / value).exists(), f"manifest path missing: {key} -> {value}")

required_caps = {
    "institution_registry", "institution_membership", "role_permission_governance", "workspace_federation",
    "workspace_relationship_policies", "platform_connection_registry", "connection_verification",
    "decision_pathway_graphs", "platform_workflow_registry", "deterministic_workflow_runs",
    "cross_repository_snapshots", "source_repository_hashes", "platform_event_ledger", "correlation_ids",
    "institution_overviews", "platform_integrity_reports", "platform_repository_export",
    "lossless_platform_restore", "wordpress_platform_hub",
}
require(required_caps.issubset(set(manifest.get("repository_capabilities", []))), "platform capabilities incomplete")

repository = read("python/global_impact_repository.py")
for marker in [
    "DATABASE_SCHEMA_VERSION = 12", "ConnectedImpactPlatformMixin",
    "012_connected_public_interest_impact_intelligence_platform.sql",
    '"bundle_version": "2.0.0"',
    '"platform_repository": self.export_platform_repository(workspace_id)',
    "self._restore_platform_repository", '"institutions": count("institutions")',
    '"platform_snapshots": count("platform_snapshots")',
]:
    require(marker in repository, f"repository contract missing: {marker}")

platform = read("python/global_impact_platform.py")
for marker in [
    'PLATFORM_VERSION = "2.0.0"', "def register_institution", "def add_institution_member",
    "def link_institution_workspace", "def check_platform_permission", "def register_platform_connection",
    "def verify_platform_connection", "def create_decision_pathway", "def create_platform_workflow",
    "def run_platform_workflow", "def emit_platform_event", "def create_platform_snapshot",
    "def platform_integrity_report", "def institution_overview", "def export_platform_repository",
    "def _restore_platform_repository",
]:
    require(marker in platform, f"platform contract missing: {marker}")

service = read("python/global_impact_service.py")
for marker in [
    'SERVICE_VERSION = "2.0.0"', "def register_institution", "def add_institution_member",
    "def link_institution_workspace", "def register_platform_connection", "def verify_platform_connection",
    "def create_decision_pathway", "def create_platform_workflow", "def run_platform_workflow",
    "def create_platform_snapshot", "def platform_repository", "def institution_overview",
]:
    require(marker in service, f"service contract missing: {marker}")

app = read("app/main.py")
for marker in [
    '"version": "2.0.0"', '"database_schema_version": 12',
    '"platform_repository_version": "2.0.0"', '"production_repository_version": "1.10.0"',
]:
    require(marker in app, f"application contract missing: {marker}")

cli = read("scripts/gic_repository.py")
for command in [
    "platform-repository", "add-institution", "add-platform-member", "link-platform-workspace",
    "add-platform-connection", "verify-platform-connection", "add-decision-pathway",
    "add-platform-workflow", "run-platform-workflow", "platform-snapshot", "institution-overview",
]:
    require(f'"{command}"' in cli or f"'{command}'" in cli, f"CLI command missing: {command}")

php = read("wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
for marker in [
    "* Version: 2.0.0", "define('GIC_DEMO_VERSION', '2.0.0')",
    "update_option('gic_repository_schema_version', 12, false)",
    "add_shortcode('global_impact_catalyst_platform_hub'", "/platform-repository",
    "/platform-institutions", "/platform-members", "/platform-connections",
    "/decision-pathways", "/platform-snapshots",
]:
    require(marker in php, f"WordPress platform contract missing: {marker}")
for table in [
    "institutions", "institution_members", "institution_workspaces", "platform_connections",
    "decision_pathways", "platform_workflows", "platform_workflow_runs", "platform_snapshots", "platform_events",
]:
    require(f"gic_repository_table('{table}')" in php, f"WordPress table missing: {table}")
for asset in ["global-impact-catalyst-platform.js", "global-impact-catalyst-platform.css"]:
    require((ROOT / "wordpress/global-impact-catalyst-demo/assets" / asset).exists(), f"WordPress asset missing: {asset}")

schema_examples = {
    "global_impact_platform_repository.schema.json": "example_global_impact_platform_repository.json",
    "global_impact_workspace_bundle.schema.json": "example_global_impact_workspace_bundle.json",
}
for schema_name, example_name in schema_examples.items():
    schema = load("schemas/" + schema_name)
    example = load("examples/" + example_name)
    require(schema.get("x-global-impact-catalyst-version") == PACKAGE, f"{schema_name} version marker missing")
    for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(example):
        errors.append(f"{example_name}: {error.message}")

migration = read("migrations/012_connected_public_interest_impact_intelligence_platform.sql")
for table in [
    "institutions", "institution_members", "institution_workspaces", "platform_connections",
    "decision_pathways", "platform_workflows", "platform_workflow_runs", "platform_snapshots", "platform_events",
]:
    require(re.search(rf"CREATE TABLE IF NOT EXISTS\s+{table}\b", migration, re.I) is not None, f"migration 12 table missing: {table}")

for path in [
    "README.md", "CHANGELOG.md", "release/v2.0.0.md",
    "docs/connected-public-interest-impact-intelligence-platform.md",
    "docs/workspace-bundles.md", "docs/database-migrations.md",
]:
    require("2.0.0" in read(path), f"v2.0.0 documentation marker missing: {path}")
require("Connected Public-Interest Impact Intelligence Platform" in read("README.md"), "README release title missing")

if errors:
    print("Global Impact Catalyst v2.0.0 release contract FAILED:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print("Global Impact Catalyst v2.0.0 release contract passed.")
