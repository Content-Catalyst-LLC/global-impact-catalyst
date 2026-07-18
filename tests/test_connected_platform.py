from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_platform import PLATFORM_VERSION, PlatformError
from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService

ROOT = Path(__file__).resolve().parents[1]
FIXED = "2026-07-18T12:00:00+00:00"


def payload():
    return json.loads((ROOT / "data/sample_global_impact_input.json").read_text())


def setup_platform(repo):
    result = ImpactApplicationService(repo).create_initiative(payload(), generated_at=FIXED, actor="owner")
    workspace_id = result["repository"]["workspace_id"]
    initiative_id = result["repository"]["initiative_id"]
    institution = repo.register_institution({"name": "Sustainable Catalyst", "slug": "sustainable-catalyst", "mission": "Public-interest impact intelligence"})
    member = repo.add_institution_member(institution["institution_id"], {
        "principal_id": "tariq", "display_name": "Tariq Ahmad", "role": "owner", "permissions": ["platform.manage"]
    })
    link = repo.link_institution_workspace(institution["institution_id"], workspace_id, relationship="owned", policy={"public_interest": True})
    return result, institution, member, link, workspace_id, initiative_id


def validate(name, document):
    schema = json.loads((ROOT / "schemas" / name).read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)


def test_migration_12_and_platform_identity(tmp_path):
    with SQLiteImpactRepository(tmp_path / "platform.sqlite3") as repo:
        assert PLATFORM_VERSION == "2.0.0"
        assert DATABASE_SCHEMA_VERSION == 12
        assert repo.schema_version == 12
        tables = {row["name"] for row in repo.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"institutions", "institution_members", "institution_workspaces", "platform_connections", "decision_pathways", "platform_workflows", "platform_workflow_runs", "platform_snapshots", "platform_events"}.issubset(tables)


def test_institution_membership_permissions_and_workspace_policy(tmp_path):
    with SQLiteImpactRepository(tmp_path / "access.sqlite3") as repo:
        _, institution, member, link, workspace_id, _ = setup_platform(repo)
        assert member["role"] == "owner"
        assert member["email_hash"] is None
        assert link["policy"]["public_interest"] is True
        assert repo.check_platform_permission(institution["institution_id"], "tariq", "anything", workspace_id=workspace_id)
        assert not repo.check_platform_permission(institution["institution_id"], "unknown", "platform.manage")


def test_connection_verification_and_integrity(tmp_path):
    with SQLiteImpactRepository(tmp_path / "connections.sqlite3") as repo:
        _, institution, _, _, workspace_id, _ = setup_platform(repo)
        connection = repo.register_platform_connection({
            "destination": "decision_studio", "connection_type": "internal_module", "contract_version": "2.0.0",
            "capabilities": ["decision_packet", "evidence_handoff"]
        }, institution_id=institution["institution_id"])
        assert connection["status"] == "configured"
        verified = repo.verify_platform_connection(connection["connection_id"])
        assert verified["status"] == "verified"
        integrity = repo.platform_integrity_report(institution["institution_id"], workspace_id=workspace_id)
        assert integrity["valid"] and integrity["verified_connection_count"] == 1


def test_decision_pathway_requires_valid_graph(tmp_path):
    with SQLiteImpactRepository(tmp_path / "pathways.sqlite3") as repo:
        _, institution, _, _, workspace_id, initiative_id = setup_platform(repo)
        pathway = repo.create_decision_pathway({
            "title": "Evidence to decision", "initiative_id": initiative_id,
            "nodes": [{"id": "evidence", "type": "evidence_repository"}, {"id": "decision", "type": "decision_studio"}],
            "edges": [{"from": "evidence", "to": "decision", "relationship": "informs"}]
        }, institution_id=institution["institution_id"], workspace_id=workspace_id)
        assert pathway["nodes"][0]["id"] == "evidence"
        with pytest.raises(PlatformError):
            repo.create_decision_pathway({"title": "Broken", "nodes": [{"id": "a"}], "edges": [{"from": "a", "to": "missing"}]}, institution_id=institution["institution_id"], workspace_id=workspace_id)


def test_workflow_orchestrates_integrity_snapshot_and_event(tmp_path):
    with SQLiteImpactRepository(tmp_path / "workflow.sqlite3") as repo:
        _, institution, _, _, workspace_id, _ = setup_platform(repo)
        workflow = repo.create_platform_workflow({
            "name": "Institutional impact review", "workflow_type": "evidence_to_decision",
            "steps": [{"type": "repository_integrity"}, {"type": "create_snapshot"}, {"type": "emit_event", "event_type": "impact.reviewed"}]
        }, institution_id=institution["institution_id"], workspace_id=workspace_id)
        run = repo.run_platform_workflow(workflow["workflow_id"], inputs={"review_cycle": "2026-Q3"})
        assert run["status"] == "completed"
        assert [step["type"] for step in run["step_results"]] == ["repository_integrity", "create_snapshot", "emit_event"]
        assert repo.repository_summary()["platform_snapshots"] == 1
        assert repo.repository_summary()["platform_events"] == 1


def test_platform_snapshot_binds_all_repository_hashes(tmp_path):
    with SQLiteImpactRepository(tmp_path / "snapshot.sqlite3") as repo:
        _, institution, _, _, workspace_id, _ = setup_platform(repo)
        snapshot = repo.create_platform_snapshot(institution["institution_id"], workspace_id)
        assert set(snapshot["source_hashes"]) == {"evidence", "registry", "measurement", "review", "analysis", "reporting", "integration", "production"}
        assert len(snapshot["snapshot_hash"]) == 64
        assert snapshot["summary"]["repository"]["database_schema_version"] == 12


def test_platform_schema_and_lossless_workspace_restore(tmp_path):
    with SQLiteImpactRepository(tmp_path / "source.sqlite3") as source:
        _, institution, _, _, workspace_id, initiative_id = setup_platform(source)
        connection = source.register_platform_connection({"destination": "knowledge_library", "connection_type": "internal_module", "contract_version": "1.0.0", "capabilities": ["citation_link"]}, institution_id=institution["institution_id"])
        source.verify_platform_connection(connection["connection_id"])
        source.create_decision_pathway({"title": "Impact evidence pathway", "initiative_id": initiative_id, "nodes": [{"id": "measure"}, {"id": "publish"}], "edges": [{"from": "measure", "to": "publish"}]}, institution_id=institution["institution_id"], workspace_id=workspace_id)
        source.create_platform_snapshot(institution["institution_id"], workspace_id)
        platform = source.export_platform_repository(workspace_id)
        bundle = source.export_workspace_bundle(workspace_id)
        validate("global_impact_platform_repository.schema.json", platform)
        validate("global_impact_workspace_bundle.schema.json", bundle)
        assert bundle["bundle_version"] == "2.0.0" and bundle["database_schema_version"] == 12

    with SQLiteImpactRepository(tmp_path / "target.sqlite3") as target:
        receipt = target.restore_workspace_bundle(bundle)
        assert receipt["status"] == "restored"
        restored = target.export_platform_repository(workspace_id)
        assert restored["integrity"]["institution_count"] == 1
        assert restored["integrity"]["connection_count"] == 1
        assert restored["integrity"]["pathway_count"] == 1
        assert restored["integrity"]["snapshot_count"] == 1
        assert target.restore_workspace_bundle(bundle)["status"] == "unchanged"


def test_application_service_platform_facade(tmp_path):
    with SQLiteImpactRepository(tmp_path / "service.sqlite3") as repo:
        service = ImpactApplicationService(repo)
        result = service.create_initiative(payload(), generated_at=FIXED)
        workspace_id = result["repository"]["workspace_id"]
        institution = service.register_institution({"name": "Public Interest Lab", "slug": "public-interest-lab"})
        service.add_institution_member(institution["institution_id"], {"principal_id": "owner", "role": "owner"})
        service.link_institution_workspace(institution["institution_id"], workspace_id)
        exported = service.platform_repository(workspace_id)
        assert exported["repository_version"] == "2.0.0"
        assert service.institution_overview(institution["institution_id"])["integrity"]["valid"]
