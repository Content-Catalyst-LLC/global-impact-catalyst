from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_integration import (
    HANDOFF_DESTINATIONS,
    IdempotencyConflictError,
    PermissionDeniedError,
    RateLimitError,
)
from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService

ROOT = Path(__file__).resolve().parents[1]
FIXED = "2026-07-17T23:00:00+00:00"


def payload():
    return json.loads((ROOT / "data/sample_global_impact_input.json").read_text())


def create(repo):
    result = ImpactApplicationService(repo).create_initiative(payload(), generated_at=FIXED, actor="owner")
    meta = result["repository"]
    return result, meta["workspace_id"], meta["initiative_id"], meta["record_id"]


def approve_publish_snapshot(repo, workspace_id, initiative_id, record_id):
    role = next(item for item in repo.list_workflow_roles(workspace_id) if item["metadata"].get("role_key") == "approver")
    assignment = repo.create_review_assignment({
        "subject_type": "contract", "subject_id": record_id,
        "reviewer_id": "approver@example.org", "role_id": role["role_id"],
    }, workspace_id=workspace_id, initiative_id=initiative_id)
    repo.submit_quality_assessment({
        "assessor_id": "approver@example.org",
        "dimensions": [{"key": "evidence", "score": 92, "maximum_score": 100},
                       {"key": "method", "score": 88, "maximum_score": 100}],
    }, workspace_id=workspace_id, initiative_id=initiative_id, assignment_id=assignment["assignment_id"])
    repo.record_approval_decision(assignment["assignment_id"], "approve", rationale="Approved for public release.", reviewer_id="approver@example.org")
    report = repo.create_report({"title": "Public Impact Report", "period_label": "2026 Q2"}, workspace_id=workspace_id, initiative_id=initiative_id)
    publication = repo.create_publication({"subject_type": "contract", "subject_id": record_id, "title": "Public Impact Profile", "release_label": "2026 Q2"}, workspace_id=workspace_id, initiative_id=initiative_id)
    publication = repo.publish(publication["publication_id"], actor="publisher")
    snapshot = repo.create_publication_snapshot(publication["publication_id"], report_id=report["report_id"], actor="publisher")
    return publication, report, snapshot


def test_migration_10_api_client_scope_and_rate_controls(tmp_path):
    with SQLiteImpactRepository(tmp_path / "api.sqlite3") as repo:
        _, workspace_id, _, _ = create(repo)
        assert DATABASE_SCHEMA_VERSION == 10 and repo.schema_version == 10
        client = repo.register_api_client({
            "name": "Decision Studio", "client_type": "service",
            "scopes": ["workspace:read", "handoffs:write"], "rate_limit_per_minute": 2,
        }, workspace_id=workspace_id, actor="owner")
        issued = client["issued_key"]
        auth = repo.authenticate_api_key(issued["api_key"], required_scope="workspace:read")
        assert auth["client_id"] == client["client_id"] and "handoffs:write" in auth["scopes"]
        repo.authenticate_api_key(issued["api_key"], required_scope="workspace:read")
        with pytest.raises(RateLimitError):
            repo.authenticate_api_key(issued["api_key"], required_scope="workspace:read")
        repo.revoke_api_key(issued["api_key_id"], actor="owner")
        with pytest.raises(Exception, match="invalid or inactive"):
            repo.authenticate_api_key(issued["api_key"])


def test_idempotency_replay_and_conflict(tmp_path):
    with SQLiteImpactRepository(tmp_path / "idempotency.sqlite3") as repo:
        _, workspace_id, _, _ = create(repo)
        client = repo.register_api_client({"name": "Importer", "scopes": ["workspace:read"]}, workspace_id=workspace_id)
        calls = {"count": 0}
        def execute():
            calls["count"] += 1
            return {"status": "created", "number": calls["count"]}
        one, replay = repo.idempotent_operation(client_id=client["client_id"], idempotency_key="request-001", operation="import", request_payload={"value": 1}, execute=execute)
        two, replay_two = repo.idempotent_operation(client_id=client["client_id"], idempotency_key="request-001", operation="import", request_payload={"value": 1}, execute=execute)
        assert not replay and replay_two and one == two and calls["count"] == 1
        with pytest.raises(IdempotencyConflictError):
            repo.idempotent_operation(client_id=client["client_id"], idempotency_key="request-001", operation="import", request_payload={"value": 2}, execute=execute)


def test_public_api_requires_published_snapshot_and_redacts_private_evidence(tmp_path):
    with SQLiteImpactRepository(tmp_path / "public.sqlite3") as repo:
        _, workspace_id, initiative_id, record_id = create(repo)
        draft = repo.create_publication({"subject_type": "contract", "subject_id": record_id, "title": "Draft profile"}, workspace_id=workspace_id, initiative_id=initiative_id)
        with pytest.raises(PermissionDeniedError):
            repo.public_publication(draft["publication_id"])
        publication, report, snapshot = approve_publish_snapshot(repo, workspace_id, initiative_id, record_id)
        public = repo.public_publication(publication["publication_id"])
        assert public["api_version"] == "v1"
        assert public["data"]["snapshot"]["snapshot_hash"] == snapshot["snapshot_hash"]
        assert public["data"]["report"]["content_hash"] == report["content_hash"]
        serialized = json.dumps(public)
        assert "content_text" not in serialized and "evidence_items" not in serialized
        catalog = repo.public_catalog(page=1, page_size=10, search="energy")
        assert catalog["meta"]["pagination"]["total"] == 1
        assert catalog["data"][0]["profile"]["indicator"]["name"]


def test_workspace_api_pagination_and_workspace_scope(tmp_path):
    with SQLiteImpactRepository(tmp_path / "workspace-api.sqlite3") as repo:
        _, workspace_id, _, _ = create(repo)
        client = repo.register_api_client({"name": "Workspace reader", "scopes": ["workspace:read"]}, workspace_id=workspace_id)
        response = repo.workspace_api_resource(api_key=client["issued_key"]["api_key"], workspace_id=workspace_id, resource="initiatives", page=1, page_size=1)
        assert response["meta"]["pagination"] == {"page": 1, "page_size": 1, "total": 1, "page_count": 1}
        other = "gic-workspace-not-authorized"
        with pytest.raises(PermissionDeniedError):
            repo.workspace_api_resource(api_key=client["issued_key"]["api_key"], workspace_id=other, resource="initiatives")


def test_governed_embed_creation_and_public_render(tmp_path):
    with SQLiteImpactRepository(tmp_path / "embed.sqlite3") as repo:
        _, workspace_id, initiative_id, record_id = create(repo)
        publication, _, snapshot = approve_publish_snapshot(repo, workspace_id, initiative_id, record_id)
        embed = repo.create_embed({
            "embed_type": "indicator_trend", "title": "Community energy impact",
            "publication_id": publication["publication_id"], "publication_snapshot_id": snapshot["snapshot_id"],
            "public_slug": "community-energy-impact",
        }, workspace_id=workspace_id, actor="editor")
        rendered = repo.render_embed(embed["public_slug"])
        assert rendered["snapshot_hash"] == snapshot["snapshot_hash"]
        assert "approved publication" in rendered["html"] and "aria-labelledby" in rendered["html"]
        assert "edit" not in rendered["html"].lower()
        draft = repo.create_publication({"subject_type": "contract", "subject_id": record_id, "title": "Draft embed"}, workspace_id=workspace_id, initiative_id=initiative_id)
        with pytest.raises(PermissionDeniedError):
            repo.create_embed({"publication_id": draft["publication_id"]}, workspace_id=workspace_id)


def test_all_platform_handoffs_are_versioned_hashed_and_idempotent(tmp_path):
    with SQLiteImpactRepository(tmp_path / "handoffs.sqlite3") as repo:
        _, workspace_id, initiative_id, _ = create(repo)
        for destination in sorted(HANDOFF_DESTINATIONS):
            handoff = repo.create_platform_handoff(destination, workspace_id=workspace_id, initiative_id=initiative_id, idempotency_key=f"{destination}-001", actor="integration")
            assert handoff["handoff_version"] == "1.9.0"
            assert handoff["payload"]["destination"] == destination
            assert handoff["integrity"]["valid"]
            replay = repo.create_platform_handoff(destination, workspace_id=workspace_id, initiative_id=initiative_id, idempotency_key=f"{destination}-001")
            assert replay["handoff_id"] == handoff["handoff_id"] and replay["idempotent_replay"]
        decision = next(item for item in repo.list_platform_handoffs(workspace_id) if item["destination"] == "decision_studio")
        assert decision["payload"]["data"]["monitoring_plan"]["observations"]
        delivered = repo.record_handoff_delivery(decision["handoff_id"], {"status": "accepted", "remote_id": "decision-42"})
        assert delivered["status"] == "delivered" and delivered["delivery_receipt"]["remote_id"] == "decision-42"


def issued_key_material_absent(serialized: str) -> bool:
    return "gic_live_" not in serialized and "key_hash" not in serialized


def test_integration_schema_and_lossless_workspace_restore(tmp_path):
    with SQLiteImpactRepository(tmp_path / "source.sqlite3") as source:
        _, workspace_id, initiative_id, record_id = create(source)
        publication, _, snapshot = approve_publish_snapshot(source, workspace_id, initiative_id, record_id)
        client = source.register_api_client({"name": "Platform Core", "scopes": ["workspace:read", "handoffs:write"]}, workspace_id=workspace_id)
        source.workspace_api_resource(api_key=client["issued_key"]["api_key"], workspace_id=workspace_id, resource="initiatives")
        source.create_embed({"publication_id": publication["publication_id"], "publication_snapshot_id": snapshot["snapshot_id"], "embed_type": "initiative_card"}, workspace_id=workspace_id)
        source.create_platform_handoff("platform_core", workspace_id=workspace_id, initiative_id=initiative_id, idempotency_key="core-001")
        integration = source.export_integration_repository(workspace_id)
        bundle = source.export_workspace_bundle(workspace_id)
        assert integration["integrity"]["valid"] and integration["privacy"]["api_key_material_exported"] is False
        assert bundle["bundle_version"] == "1.9.0" and bundle["database_schema_version"] == 10
        serialized_clients = json.dumps(integration["api_clients"])
        assert issued_key_material_absent(serialized_clients)
        Draft202012Validator(json.loads((ROOT / "schemas/global_impact_integration_repository.schema.json").read_text()), format_checker=FormatChecker()).validate(integration)
        Draft202012Validator(json.loads((ROOT / "schemas/global_impact_workspace_bundle.schema.json").read_text()), format_checker=FormatChecker()).validate(bundle)
    with SQLiteImpactRepository(tmp_path / "target.sqlite3") as target:
        assert target.restore_workspace_bundle(bundle)["status"] == "restored"
        assert target.restore_workspace_bundle(bundle)["status"] == "unchanged"
        restored = target.export_integration_repository(workspace_id)
        assert restored["integrity"] == integration["integrity"]
        assert restored["platform_handoffs"][0]["payload_hash"] == integration["platform_handoffs"][0]["payload_hash"]
        assert restored["embeds"][0]["content_hash"] == integration["embeds"][0]["content_hash"]
        assert restored["integrity"]["access_log_count"] == 1
        assert restored["api_access_log"][0]["api_key_id"] == integration["api_access_log"][0]["api_key_id"]
        restored_key = target.connection.execute("SELECT revoked_at,metadata_json FROM api_keys WHERE api_key_id=?", (restored["api_access_log"][0]["api_key_id"],)).fetchone()
        assert restored_key["revoked_at"] and json.loads(restored_key["metadata_json"])["authentication_disabled"] is True
