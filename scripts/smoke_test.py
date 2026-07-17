#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")


def run(*args: str, stdout=None) -> None:
    subprocess.run(args, cwd=ROOT, check=True, env=SUBPROCESS_ENV, stdout=stdout)


def validate(document: dict, schema_name: str) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document))
    assert not errors, "\n".join(error.message for error in errors[:10])


def main() -> int:
    if os.environ.get("GIC_SKIP_PYTEST") == "1":
        print("INFO: pytest suite skipped; running deterministic installed-repository gates.")
    else:
        run(sys.executable, "-m", "pytest", "-q")
    run(sys.executable, "scripts/check_contracts.py")

    if shutil.which("node"):
        run("node", "scripts/check_browser_parity.js")
        for asset in (
            "global-impact-catalyst-demo.js",
            "global-impact-catalyst-workspace.js",
            "global-impact-catalyst-evidence.js",
            "global-impact-catalyst-registry.js",
        ):
            run("node", "--check", f"wordpress/global-impact-catalyst-demo/assets/{asset}")
    else:
        print("INFO: Node unavailable; browser checks skipped by portable smoke test.")

    if shutil.which("php"):
        run("php", "-l", "wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
        run("php", "scripts/check_wordpress_instances.php")
    else:
        print("INFO: PHP unavailable; WordPress checks skipped by portable smoke test.")

    with tempfile.TemporaryDirectory(prefix="gic-v140-") as temp:
        directory = Path(temp)
        contract_path = directory / "contract.json"
        brief_path = directory / "brief.md"
        database = directory / "impact.sqlite3"
        restored_database = directory / "restored.sqlite3"
        bundle_path = directory / "workspace-bundle.json"
        registry_path = directory / "indicator-registry.json"
        backup = directory / "impact-backup.sqlite3"

        run(
            sys.executable,
            "python/global_impact_core.py",
            "--input", "data/sample_global_impact_input.json",
            "--output", str(contract_path),
            "--markdown", str(brief_path),
            "--generated-at", "2026-07-17T18:00:00+00:00",
        )
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        assert contract["contract_version"] == "1.1.0"
        assert contract["derived"]["metrics"]["progress_to_target_percent"] == 60.0
        validate(contract, "global_impact_contract.schema.json")

        run(sys.executable, "scripts/gic_repository.py", "--database", str(database), "init", stdout=subprocess.DEVNULL)
        run(
            sys.executable,
            "scripts/gic_repository.py",
            "--database", str(database),
            "create",
            "--input", "data/sample_global_impact_input.json",
            "--generated-at", "2026-07-17T18:00:00+00:00",
            stdout=subprocess.DEVNULL,
        )

        from python.global_impact_repository import SQLiteImpactRepository
        from python.global_impact_service import ImpactApplicationService

        with SQLiteImpactRepository(database) as repository:
            summary = repository.repository_summary()
            assert summary["database_schema_version"] == 5
            assert summary["contracts"] == 1
            assert summary["sources"] == 1
            assert summary["source_versions"] == 1
            assert summary["provenance_edges"] >= 9
            assert summary["units"] >= 18
            assert summary["indicator_definitions"] == 1
            assert summary["baseline_models"] == 1
            assert summary["target_models"] == 1
            assert summary["method_definitions"] == 1
            assert summary["indicator_registry_bindings"] == 1

            workspace_id = repository.list_entities("workspace")[0]["entity_id"]
            initiative_id = repository.list_entities("initiative")[0]["entity_id"]
            stored = repository.get_contract(initiative_id=initiative_id)
            source = repository.evidence_chain(initiative_id)["sources"][0]

            evidence = repository.capture_evidence(
                source["source_id"],
                evidence_type="quotation",
                title="Portable release evidence",
                locator="p. 14",
                exact_quote="Average monthly bills declined by eighteen dollars.",
                captured_by="release-smoke",
            )
            repository.register_dataset(
                source["source_id"],
                {
                    "title": "Portable release dataset",
                    "version": "1",
                    "license": "restricted-internal",
                    "checksum_value": "a" * 64,
                    "schema_fingerprint": "b" * 64,
                    "row_count": 420,
                    "column_count": 18,
                },
                actor="release-smoke",
            )
            claim_id = stored["contract"]["derived"]["claims"][0]["id"]
            repository.link_claim_evidence(
                claim_id,
                evidence["evidence_id"],
                relationship="supports",
                strength="direct",
                linked_by="release-smoke",
            )

            assert repository.convert_value(2, "MWh", "kWh") == 2000.0
            assert repository.convert_value(25, "%", "ratio") == 0.25
            custom_unit = repository.register_unit(
                {"code": "person-day", "name": "Person day", "dimension": "labor"},
                workspace_id=workspace_id,
                actor="release-smoke",
            )
            assert custom_unit["revision"] == 1

            indicator = repository.register_indicator_definition(
                {
                    "name": "Energy saved",
                    "description": "Metered avoided consumption.",
                    "unit": "kWh",
                    "direction": "higher_is_better",
                    "aggregation_method": "sum",
                    "version_label": "1.0",
                },
                workspace_id=workspace_id,
                actor="release-smoke",
            )
            baseline = repository.register_baseline_model(
                {"name": "Three-period average", "method_type": "period_average", "unit": "kWh", "minimum_observations": 3},
                workspace_id=workspace_id,
                actor="release-smoke",
            )
            target = repository.register_target_model(
                {"name": "Linear energy path", "target_type": "trajectory", "start_value": 100, "end_value": 160, "trajectory_type": "linear", "unit": "kWh"},
                workspace_id=workspace_id,
                actor="release-smoke",
            )
            method = repository.register_method_definition(
                {
                    "name": "Metered energy comparison",
                    "method_kind": "measurement",
                    "design_type": "before_after",
                    "description": "Compares normalized meter periods.",
                    "input_requirements": ["meter readings"],
                    "quality_profile": {"reproducibility": "documented"},
                    "limitations": ["weather adjustment remains material"],
                },
                workspace_id=workspace_id,
                actor="release-smoke",
            )
            assert indicator["current_version"] == 1
            assert repository.compute_baseline(baseline["baseline_model_id"], [100, 120, 140])["value"] == 120
            assert repository.evaluate_target(target["target_model_id"], progress_fraction=0.5)["value"] == 130
            assert method["current_version"] == 1

            chain = repository.evidence_chain(initiative_id)
            assert chain["integrity"]["valid"]
            assert chain["integrity"]["evidence_count"] == 1
            assert chain["integrity"]["dataset_count"] == 1
            assert chain["integrity"]["claim_link_count"] == 1
            validate(chain, "global_impact_evidence_chain.schema.json")

            evidence_export = repository.export_evidence_repository(workspace_id)
            validate(evidence_export, "global_impact_evidence_repository.schema.json")

            registry = repository.export_indicator_registry(workspace_id)
            registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
            assert registry["registry_version"] == "1.4.0"
            assert registry["integrity"]["valid"]
            assert registry["integrity"]["unit_count"] >= 19
            assert registry["integrity"]["indicator_definition_count"] >= 2
            validate(registry, "global_impact_indicator_registry.schema.json")

            bundle = repository.export_workspace_bundle(workspace_id)
            bundle_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
            assert bundle["bundle_version"] == "1.4.0"
            assert bundle["database_schema_version"] == 5
            validate(bundle, "global_impact_workspace_bundle.schema.json")
            repository.backup_database(backup)

        assert backup.exists() and backup.stat().st_size > 0

        with SQLiteImpactRepository(restored_database) as repository:
            result = repository.restore_workspace_bundle(json.loads(bundle_path.read_text(encoding="utf-8")))
            assert result["status"] == "restored"
            restored_registry = repository.export_indicator_registry(workspace_id)
            assert restored_registry["integrity"] == registry["integrity"]
            restored_chain = repository.evidence_chain(initiative_id)
            assert restored_chain["integrity"]["valid"]
            repeated = repository.restore_workspace_bundle(json.loads(bundle_path.read_text(encoding="utf-8")))
            assert repeated["status"] == "unchanged"

        legacy = json.loads((ROOT / "contracts/legacy/legacy-v1.0.1-record.json").read_text(encoding="utf-8"))
        with SQLiteImpactRepository(database) as repository:
            service = ImpactApplicationService(repository)
            imported = service.import_document(legacy, generated_at="2026-07-17T18:00:00+00:00")
            repeated = service.import_document(legacy, generated_at="2026-07-17T18:00:00+00:00")
            assert imported.status == "imported"
            assert repeated.status == "unchanged"

    print("Global Impact Catalyst v1.4.0 portable release smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
