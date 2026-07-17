#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.4.0."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "1.4.0"
CONTRACT = "1.1.0"
EVIDENCE = "1.3.0"
DATABASE = 5
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


manifest = json.loads(read("global_impact_catalyst_manifest.json"))
for key, value in (
    ("version", PACKAGE),
    ("contract_version", CONTRACT),
    ("schema_version", CONTRACT),
    ("database_schema_version", DATABASE),
    ("workspace_bundle_version", PACKAGE),
    ("evidence_chain_version", EVIDENCE),
    ("indicator_registry_version", PACKAGE),
    ("formula_language", "gic-expression-1.0"),
    ("shortcode", "[global_impact_catalyst_demo]"),
    ("workspace_shortcode", "[global_impact_catalyst_workspace]"),
    ("evidence_shortcode", "[global_impact_catalyst_evidence_ledger]"),
    ("indicator_registry_shortcode", "[global_impact_catalyst_indicator_registry]"),
):
    require(manifest.get(key) == value, f"manifest {key} mismatch")

path_keys = (
    "core_path", "browser_core_path", "plugin_path", "input_schema_path", "schema_path",
    "compatibility_schema_path", "validation_schema_path", "fixtures_path", "legacy_fixture_path",
    "methodology_path", "contract_reference_path", "validation_rules_path", "migration_path",
    "repository_path", "service_path", "repository_cli_path", "workspace_bundle_schema_path",
    "database_migrations_path", "persistent_repository_doc_path", "database_migrations_doc_path",
    "workspace_bundles_doc_path", "wordpress_workspace_doc_path", "evidence_chain_schema_path",
    "evidence_repository_schema_path", "evidence_repository_doc_path", "evidence_chain_doc_path",
    "source_integrity_doc_path", "evidence_chain_example_path", "evidence_repository_example_path",
    "indicator_registry_module_path", "indicator_registry_schema_path", "indicator_registry_doc_path",
    "unit_governance_doc_path", "baseline_target_methods_doc_path", "indicator_registry_example_path",
    "database_migration_5",
)
for key in path_keys:
    require(key in manifest, f"manifest key missing: {key}")
    if key in manifest:
        require((ROOT / manifest[key]).exists(), f"manifest path missing: {key} -> {manifest[key]}")

required_caps = {
    "sqlite", "migrations", "optimistic_concurrency", "workspace_bundle", "database_backup",
    "source_registry", "source_versions", "sha256_integrity", "evidence_capture", "dataset_registry",
    "provenance_graph", "claim_evidence_links", "contradiction_visibility",
    "standard_unit_registry", "custom_units", "unit_conversion", "unit_compatibility",
    "indicator_definition_registry", "immutable_indicator_versions", "safe_formula_language",
    "baseline_models", "baseline_computation", "target_models", "target_trajectories",
    "method_registry", "method_quality_profiles", "indicator_registry_bindings",
    "indicator_registry_export",
}
require(required_caps.issubset(set(manifest.get("repository_capabilities", []))), "manifest repository capabilities incomplete")

repository = read("python/global_impact_repository.py")
for needle in (
    "DATABASE_SCHEMA_VERSION = 5", "IndicatorRegistryMixin", "005_indicator_registry_units_baselines_targets_methods.sql",
    "self._seed_standard_units()", "self._materialize_contract_registry", '"bundle_version": "1.4.0"',
    '"indicator_registry": self.export_indicator_registry(workspace_id)', "self._restore_indicator_registry",
    '"indicator_registry_bindings": count("indicator_registry_bindings")',
):
    require(needle in repository, f"repository contract missing: {needle}")

registry = read("python/global_impact_registry.py")
for needle in (
    'REGISTRY_VERSION = "1.4.0"', 'FORMULA_LANGUAGE = "gic-expression-1.0"',
    "def validate_formula_expression", "def evaluate_formula_expression", "def register_unit",
    "def convert_value", "def register_indicator_definition", "def register_baseline_model",
    "def compute_baseline", "def register_target_model", "def evaluate_target",
    "def register_method_definition", "def bind_indicator_registry", "def export_indicator_registry",
    "def _restore_indicator_registry",
):
    require(needle in registry, f"indicator registry contract missing: {needle}")
require(registry.count('\"unit_id\": \"gic-unit-') >= 18, "standard unit seed set must contain at least 18 units")

service = read("python/global_impact_service.py")
for needle in (
    'SERVICE_VERSION = "1.4.0"', "def register_unit", "def register_indicator_definition",
    "def register_baseline_model", "def register_target_model", "def register_method_definition",
    "def indicator_registry",
):
    require(needle in service, f"service contract missing: {needle}")

application = read("app/main.py")
for needle in ('"version": "1.4.0"', '"database_schema_version": 5', '"indicator_registry_version": "1.4.0"'):
    require(needle in application, f"application health contract missing: {needle}")

cli = read("scripts/gic_repository.py")
for command in (
    "units", "add-unit", "indicators", "add-indicator", "add-baseline", "compute-baseline",
    "add-target", "evaluate-target", "add-method", "indicator-registry",
):
    require(f"'{command}'" in cli, f"CLI command missing: {command}")

assets = ROOT / "wordpress/global-impact-catalyst-demo/assets"
for asset in (
    "global-impact-catalyst-demo.js", "global-impact-catalyst-demo.css",
    "global-impact-catalyst-workspace.js", "global-impact-catalyst-workspace.css",
    "global-impact-catalyst-evidence.js", "global-impact-catalyst-evidence.css",
    "global-impact-catalyst-registry.js", "global-impact-catalyst-registry.css",
):
    require((assets / asset).exists() and (assets / asset).stat().st_size > 100, f"WordPress asset missing or empty: {asset}")

registry_js = read("wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-registry.js")
for needle in (
    "data-gic-indicator-registry", "indicator-registry", "indicator-definitions", "baseline-models",
    "target-models", "method-definitions",
):
    require(needle in registry_js, f"registry client missing: {needle}")

plugin = read("wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
header = re.search(r"^ \* Version:\s*([^\s]+)", plugin, re.MULTILINE)
constant = re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)", plugin)
require(bool(header) and header.group(1) == PACKAGE, "WordPress plugin header version mismatch")
require(bool(constant) and constant.group(1) == PACKAGE, "WordPress plugin constant version mismatch")
for needle in (
    "add_shortcode('global_impact_catalyst_demo'", "add_shortcode('global_impact_catalyst_workspace'",
    "add_shortcode('global_impact_catalyst_evidence_ledger'", "add_shortcode('global_impact_catalyst_indicator_registry'",
    "gic_registry_seed_units", "gic_registry_materialize_contract", "gic_registry_export",
    "gic_registry_register_routes", "'/indicator-registry'", "'/units'", "'/indicator-definitions'",
    "'/baseline-models'", "'/target-models'", "'/method-definitions'",
    "gic_repository_table('indicator_bindings')", "gic_repository_table('method_versions')",
):
    require(needle in plugin, f"WordPress registry contract missing: {needle}")

for name in (
    "global_impact_input.schema.json", "global_impact_contract.schema.json",
    "global_impact_record.schema.json", "global_impact_validation_result.schema.json",
):
    schema = json.loads(read("schemas/" + name))
    require(schema.get("x-global-impact-catalyst-version") == CONTRACT, f"canonical schema version mismatch: {name}")
    require(f"/{CONTRACT}/" in schema.get("$id", ""), f"canonical schema ID not versioned: {name}")
for name in ("global_impact_evidence_chain.schema.json", "global_impact_evidence_repository.schema.json"):
    schema = json.loads(read("schemas/" + name))
    require(schema.get("x-global-impact-catalyst-version") == EVIDENCE, f"evidence schema version mismatch: {name}")
    require(f"/{EVIDENCE}/" in schema.get("$id", ""), f"evidence schema ID mismatch: {name}")
for name in ("global_impact_workspace_bundle.schema.json", "global_impact_indicator_registry.schema.json"):
    schema = json.loads(read("schemas/" + name))
    require(schema.get("x-global-impact-catalyst-version") == PACKAGE, f"v1.4 schema version mismatch: {name}")
    require(f"/{PACKAGE}/" in schema.get("$id", ""), f"v1.4 schema ID mismatch: {name}")

fixtures = sorted((ROOT / "contracts/fixtures").glob("*.json"))
require(len(fixtures) >= 15, "canonical fixture suite must contain at least 15 fixtures")
for path in fixtures:
    fixture = json.loads(path.read_text())
    require(fixture.get("expected", {}).get("contract_version") == CONTRACT, f"fixture contract version mismatch: {path.name}")

migration_names = [p.name for p in sorted((ROOT / "migrations").glob("*.sql"))]
require(migration_names == [
    "001_core_repository.sql", "002_portfolios_and_autosave.sql", "003_imports_audit_and_bundles.sql",
    "004_sources_provenance_evidence.sql", "005_indicator_registry_units_baselines_targets_methods.sql",
], "database migration inventory mismatch")

changelog = read("CHANGELOG.md")
require("## [1.4.0]" in changelog, "CHANGELOG missing v1.4.0")
require((ROOT / "release/v1.4.0.md").exists(), "v1.4.0 release notes missing")
readme = read("README.md")
for needle in (
    "Indicator Registry, Units, Baselines, Targets, and Methods", "gic-expression-1.0",
    "[global_impact_catalyst_indicator_registry]", "canonical calculation contract remains v1.1.0",
):
    require(needle in readme, f"README section missing: {needle}")
for doc in (
    "docs/indicator-registry.md", "docs/unit-governance.md", "docs/baselines-targets-methods.md",
    "docs/sources-provenance-evidence.md", "docs/evidence-chain.md", "docs/source-integrity.md",
    "docs/persistent-repository.md", "docs/database-migrations.md", "docs/workspace-bundles.md",
    "docs/wordpress-workspace.md",
):
    require((ROOT / doc).exists() and (ROOT / doc).stat().st_size > 500, f"document incomplete: {doc}")
for example in (
    "examples/example_global_impact_indicator_registry.json", "examples/example_global_impact_workspace_bundle.json",
    "examples/example_global_impact_evidence_chain.json", "examples/example_global_impact_evidence_repository.json",
):
    require((ROOT / example).exists() and (ROOT / example).stat().st_size > 100, f"example incomplete: {example}")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)
print("Global Impact Catalyst v1.4.0 release contract passed.")
