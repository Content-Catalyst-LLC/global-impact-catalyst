from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService

ROOT = Path(__file__).resolve().parents[1]
FIXED = "2026-07-17T23:30:00+00:00"


def payload():
    return json.loads((ROOT / "data/sample_global_impact_input.json").read_text())


def create(repo):
    result = ImpactApplicationService(repo).create_initiative(payload(), generated_at=FIXED, actor="owner")
    meta = result["repository"]
    return result, meta["workspace_id"], meta["initiative_id"]


def validate(name, document):
    schema = json.loads((ROOT / "schemas" / name).read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)


def test_migration_11_seeds_locales_and_health_contract(tmp_path):
    with SQLiteImpactRepository(tmp_path / "production.sqlite3") as repo:
        assert DATABASE_SCHEMA_VERSION == 12 and repo.schema_version == 12
        assert [item["locale_code"] for item in repo.list_locales()] == ["en-US", "es", "fr"]
        assert repo.translate("status.ready", locale_code="es") == "Listo"
        assert repo.translate("unknown.key", locale_code="fr", default="Fallback") == "Fallback"


def test_custom_locale_fallback_and_rtl(tmp_path):
    with SQLiteImpactRepository(tmp_path / "locale.sqlite3") as repo:
        locale = repo.register_locale({
            "locale_code": "ar", "name": "العربية", "direction": "rtl", "fallback_locale": "en-US",
            "translations": {"status.ready": "جاهز"},
        })
        assert locale["direction"] == "rtl"
        assert repo.translate("status.ready", locale_code="ar") == "جاهز"
        assert repo.translate("offline.available", locale_code="ar") == "Available offline"


def test_offline_package_is_hash_bound_and_localized(tmp_path):
    with SQLiteImpactRepository(tmp_path / "offline.sqlite3") as repo:
        _, workspace_id, _ = create(repo)
        package = repo.create_offline_package(workspace_id, locale_code="es", generated_at=FIXED)
        assert package["package_version"] == "1.10.0"
        assert package["manifest"]["contract_count"] == 1
        assert package["payload"]["translations"]["status.ready"] == "Listo"
        assert package["integrity"]["valid"]


def test_offline_change_applies_only_at_matching_revision(tmp_path):
    with SQLiteImpactRepository(tmp_path / "sync.sqlite3") as repo:
        created, workspace_id, initiative_id = create(repo)
        initiative = repo.get_entity("initiative", initiative_id)
        queued = repo.queue_offline_change({
            "entity_type": "initiative", "entity_id": initiative_id, "operation": "update",
            "base_revision": initiative["revision"], "payload": {"name": "Offline updated initiative"},
        }, workspace_id=workspace_id, device_id="tablet-01")
        applied = repo.apply_offline_change(queued["change_id"])
        assert applied["change"]["status"] == "applied"
        assert applied["entity"]["name"] == "Offline updated initiative"

        stale = repo.queue_offline_change({
            "entity_type": "initiative", "entity_id": initiative_id, "operation": "update",
            "base_revision": 1, "payload": {"name": "Stale edit"},
        }, workspace_id=workspace_id, device_id="tablet-02")
        conflict = repo.apply_offline_change(stale["change_id"])
        assert conflict["status"] == "conflict"
        assert conflict["conflict"]["type"] == "revision_conflict"


def test_accessibility_audit_blocks_serious_findings(tmp_path):
    with SQLiteImpactRepository(tmp_path / "a11y.sqlite3") as repo:
        _, workspace_id, _ = create(repo)
        blocked = repo.record_accessibility_audit({
            "surface": "reporting_studio", "standard": "WCAG-2.2", "standard_level": "AA",
            "findings": [{"rule": "keyboard", "severity": "serious", "status": "open"}],
            "tested_by": "accessibility-reviewer",
        }, workspace_id=workspace_id)
        assert blocked["status"] == "needs_remediation" and blocked["score"] == 85
        passed = repo.record_accessibility_audit({
            "surface": "reporting_studio", "standard": "WCAG-2.2", "standard_level": "AA",
            "findings": [{"rule": "keyboard", "severity": "serious", "status": "resolved"}],
            "tested_by": "accessibility-reviewer",
        }, workspace_id=workspace_id)
        assert passed["status"] == "pass" and passed["score"] == 100


def test_security_backup_and_verified_recovery(tmp_path):
    database = tmp_path / "source.sqlite3"
    with SQLiteImpactRepository(database) as repo:
        _, workspace_id, _ = create(repo)
        policy = repo.set_security_policy({"minimum_key_rotation_days": 60, "session_timeout_minutes": 30}, workspace_id=workspace_id)
        assert policy["transport_security_required"] and policy["minimum_key_rotation_days"] == 60
        plan = repo.create_backup_plan({"name": "Nightly", "schedule": "daily", "retention_count": 14}, workspace_id=workspace_id)
        run = repo.run_backup(workspace_id, tmp_path / "backup.sqlite3", plan_id=plan["plan_id"])
        assert run["status"] == "verified" and run["verification"]["sqlite_integrity"]
        recovery = repo.verify_recovery(run["backup_run_id"], actor="operator")
        assert recovery["status"] == "passed" and all(recovery["checks"].values())


def test_release_readiness_requires_audit_and_recovery(tmp_path):
    database = tmp_path / "readiness.sqlite3"
    with SQLiteImpactRepository(database) as repo:
        _, workspace_id, _ = create(repo)
        repo.set_security_policy({}, workspace_id=workspace_id)
        blocked = repo.evaluate_release_readiness(workspace_id)
        assert blocked["status"] == "blocked"
        repo.record_accessibility_audit({"surface": "all", "findings": [], "tested_by": "reviewer"}, workspace_id=workspace_id)
        run = repo.run_backup(workspace_id, tmp_path / "ready-backup.sqlite3")
        repo.verify_recovery(run["backup_run_id"])
        environment = repo.register_deployment_environment({
            "name": "Production", "environment_type": "production", "base_url": "https://example.org",
            "runtime": {"python": "3.13", "php": "8.2"}, "controls": {"https": True, "backups": True},
        }, workspace_id=workspace_id)
        ready = repo.evaluate_release_readiness(workspace_id, environment_id=environment["environment_id"])
        assert ready["status"] == "ready" and ready["score"] == 100


def test_production_schema_and_lossless_workspace_restore(tmp_path):
    source_path = tmp_path / "source.sqlite3"
    with SQLiteImpactRepository(source_path) as source:
        _, workspace_id, _ = create(source)
        source.register_locale({"locale_code": "de", "name": "Deutsch", "translations": {"status.ready": "Bereit"}}, workspace_id=workspace_id)
        source.create_offline_package(workspace_id, locale_code="de", generated_at=FIXED)
        source.record_accessibility_audit({"surface": "all", "findings": [], "tested_by": "reviewer"}, workspace_id=workspace_id)
        source.set_security_policy({}, workspace_id=workspace_id)
        run = source.run_backup(workspace_id, tmp_path / "restore-source-backup.sqlite3")
        source.verify_recovery(run["backup_run_id"])
        source.evaluate_release_readiness(workspace_id)
        production = source.export_production_repository(workspace_id)
        bundle = source.export_workspace_bundle(workspace_id)
        validate("global_impact_production_repository.schema.json", production)
        validate("global_impact_workspace_bundle.schema.json", bundle)
        assert bundle["bundle_version"] == "2.0.0" and bundle["database_schema_version"] == 12

    with SQLiteImpactRepository(tmp_path / "target.sqlite3") as target:
        restored = target.restore_workspace_bundle(bundle)
        assert restored["status"] == "restored"
        restored_production = target.export_production_repository(workspace_id)
        assert restored_production["integrity"]["offline_package_count"] == 1
        assert restored_production["integrity"]["passed_recovery_count"] == 1
        assert target.restore_workspace_bundle(bundle)["status"] == "unchanged"
