from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_review import WorkflowGateError
from python.global_impact_service import ImpactApplicationService

ROOT = Path(__file__).resolve().parents[1]
FIXED = "2026-07-17T18:00:00+00:00"


def payload():
    return json.loads((ROOT / "data/sample_global_impact_input.json").read_text())


def create(repo: SQLiteImpactRepository):
    result = ImpactApplicationService(repo).create_initiative(payload(), generated_at=FIXED, actor="owner")
    return result, result["repository"]["workspace_id"], result["repository"]["initiative_id"], result["repository"]["record_id"]


def approver_role(repo: SQLiteImpactRepository, workspace_id: str):
    return next(role for role in repo.list_workflow_roles(workspace_id) if role["metadata"].get("role_key") == "approver")


def test_migration_7_materializes_roles_and_contract_revision(tmp_path):
    with SQLiteImpactRepository(tmp_path / "workflow.sqlite3") as repo:
        created, workspace_id, initiative_id, record_id = create(repo)
        assert DATABASE_SCHEMA_VERSION == 11
        assert repo.schema_version == 11
        summary = repo.repository_summary()
        assert summary["workflow_roles"] == 5
        assert summary["workflow_revisions"] == 1
        revision = repo.list_workflow_revisions("contract", record_id)[0]
        assert revision["revision_number"] == 1
        assert revision["change_type"] == "create"
        assert revision["snapshot"] == created["contract"]
        workflow = repo.export_review_workflow(workspace_id)
        assert workflow["workflow_version"] == "1.6.0"
        assert workflow["integrity"]["valid"] is True
        assert workflow["integrity"]["revision_count"] == 1


def test_review_comments_and_quality_gate_approval(tmp_path):
    with SQLiteImpactRepository(tmp_path / "review.sqlite3") as repo:
        _, workspace_id, initiative_id, record_id = create(repo)
        role = approver_role(repo, workspace_id)
        assignment = repo.create_review_assignment({
            "subject_type": "contract", "subject_id": record_id,
            "reviewer_id": "reviewer@example.org", "role_id": role["role_id"], "priority": "high",
        }, workspace_id=workspace_id, initiative_id=initiative_id, actor="owner")
        assignment = repo.update_review_assignment_status(assignment["assignment_id"], "in_review", actor="reviewer@example.org")
        comment = repo.add_review_comment(assignment["assignment_id"], {
            "author_id": "reviewer@example.org", "body": "Document the seasonal limitation."
        })
        repo.submit_quality_assessment({
            "subject_type": "contract", "subject_id": record_id, "assessor_id": "reviewer@example.org",
            "dimensions": [
                {"key": "evidence", "score": 80, "maximum_score": 100, "weight": 2, "finding": "Source is traceable."},
                {"key": "method", "score": 70, "maximum_score": 100, "weight": 1, "finding": "Limitations should be clearer."},
            ],
        }, workspace_id=workspace_id, initiative_id=initiative_id, assignment_id=assignment["assignment_id"])
        with pytest.raises(WorkflowGateError, match="comments remain open"):
            repo.record_approval_decision(
                assignment["assignment_id"], "approve", rationale="Ready", reviewer_id="reviewer@example.org",
                actor="reviewer@example.org",
            )
        repo.resolve_review_comment(comment["comment_id"], actor="owner")
        decision = repo.record_approval_decision(
            assignment["assignment_id"], "approve", rationale="Evidence and method are adequate.",
            conditions=["Retain the limitations note"], reviewer_id="reviewer@example.org", actor="reviewer@example.org",
        )
        assert decision["decision"] == "approve"
        assert repo.get_review_assignment(assignment["assignment_id"])["status"] == "approved"
        assessment = repo.list_quality_assessments(assignment_id=assignment["assignment_id"])[0]
        assert assessment["score"] == pytest.approx(76.67)
        assert assessment["grade"] == "strong"


def test_quality_below_threshold_blocks_approval(tmp_path):
    with SQLiteImpactRepository(tmp_path / "quality.sqlite3") as repo:
        _, workspace_id, initiative_id, record_id = create(repo)
        role = approver_role(repo, workspace_id)
        assignment = repo.create_review_assignment({
            "subject_type": "contract", "subject_id": record_id,
            "reviewer_id": "reviewer@example.org", "role_id": role["role_id"],
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        repo.submit_quality_assessment({
            "assessor_id": "reviewer@example.org",
            "dimensions": [{"key": "evidence", "score": 45, "maximum_score": 100}],
        }, workspace_id=workspace_id, initiative_id=initiative_id, assignment_id=assignment["assignment_id"])
        with pytest.raises(WorkflowGateError, match="adequate quality score"):
            repo.record_approval_decision(
                assignment["assignment_id"], "approve", rationale="Attempted approval",
                reviewer_id="reviewer@example.org", actor="reviewer@example.org",
            )
        decision = repo.record_approval_decision(
            assignment["assignment_id"], "request_changes", rationale="Improve source coverage.",
            reviewer_id="reviewer@example.org", actor="reviewer@example.org",
        )
        assert decision["decision"] == "request_changes"
        assert repo.get_review_assignment(assignment["assignment_id"])["status"] == "changes_requested"


def test_contract_correction_creates_immutable_revision_history(tmp_path):
    with SQLiteImpactRepository(tmp_path / "correction.sqlite3") as repo:
        created, workspace_id, initiative_id, record_id = create(repo)
        correction = repo.open_correction({
            "subject_type": "contract", "subject_id": record_id, "severity": "material",
            "reason": "The method limitation omitted seasonality.",
            "proposed_changes": {"facts.methods[0].description": "Add seasonality limitation."},
        }, workspace_id=workspace_id, initiative_id=initiative_id, actor="reviewer")
        corrected = copy.deepcopy(created["contract"])
        corrected["facts"]["methods"][0]["description"] += " Seasonal conditions may affect observed bills."
        applied = repo.apply_contract_correction(
            correction["correction_id"], corrected, expected_contract_revision=1,
            actor="owner", resolution_notes="Seasonality limitation added.",
        )
        assert applied["correction"]["status"] == "applied"
        history = repo.list_workflow_revisions("contract", record_id)
        assert [item["revision_number"] for item in history] == [1, 2]
        assert history[0]["content_hash"] != history[1]["content_hash"]
        assert history[1]["previous_content_hash"] == history[0]["content_hash"]
        assert history[0]["snapshot"]["facts"]["methods"][0]["description"] != history[1]["snapshot"]["facts"]["methods"][0]["description"]


def _approve_contract(repo: SQLiteImpactRepository, workspace_id: str, initiative_id: str, record_id: str):
    role = approver_role(repo, workspace_id)
    assignment = repo.create_review_assignment({
        "subject_type": "contract", "subject_id": record_id,
        "reviewer_id": "approver@example.org", "role_id": role["role_id"],
    }, workspace_id=workspace_id, initiative_id=initiative_id)
    assessment = repo.submit_quality_assessment({
        "assessor_id": "approver@example.org",
        "dimensions": [
            {"key": "evidence", "score": 85, "maximum_score": 100},
            {"key": "method", "score": 80, "maximum_score": 100},
            {"key": "traceability", "score": 90, "maximum_score": 100},
        ],
    }, workspace_id=workspace_id, initiative_id=initiative_id, assignment_id=assignment["assignment_id"])
    decision = repo.record_approval_decision(
        assignment["assignment_id"], "approve", rationale="Approved for publication.",
        reviewer_id="approver@example.org", actor="approver@example.org",
    )
    return assignment, assessment, decision


def test_publication_controls_and_withdrawal_history(tmp_path):
    with SQLiteImpactRepository(tmp_path / "publication.sqlite3") as repo:
        _, workspace_id, initiative_id, record_id = create(repo)
        draft = repo.create_publication({
            "subject_type": "contract", "subject_id": record_id,
            "title": "Community Energy Retrofit Impact Brief", "release_label": "2026 Q2",
        }, workspace_id=workspace_id, initiative_id=initiative_id, actor="publisher")
        with pytest.raises(WorkflowGateError, match="approval decision"):
            repo.publish(draft["publication_id"], actor="publisher")
        _, assessment, decision = _approve_contract(repo, workspace_id, initiative_id, record_id)
        published = repo.publish(draft["publication_id"], actor="publisher")
        assert published["publication_status"] == "published"
        assert published["approved_decision_id"] == decision["decision_id"]
        assert published["quality_assessment_id"] == assessment["assessment_id"]
        assert [event["event_type"] for event in published["events"]] == ["created", "published"]
        withdrawn = repo.withdraw_publication(
            draft["publication_id"], reason="A material correction is under review.", actor="publisher"
        )
        assert withdrawn["publication_status"] == "withdrawn"
        assert withdrawn["withdrawal_reason"] == "A material correction is under review."
        assert [event["event_type"] for event in withdrawn["events"]] == ["created", "published", "withdrawn"]


def test_open_correction_and_changed_content_block_publication(tmp_path):
    with SQLiteImpactRepository(tmp_path / "publication-gates.sqlite3") as repo:
        created, workspace_id, initiative_id, record_id = create(repo)
        _approve_contract(repo, workspace_id, initiative_id, record_id)
        draft = repo.create_publication({"subject_type": "contract", "subject_id": record_id, "title": "Brief"}, workspace_id=workspace_id, initiative_id=initiative_id)
        correction = repo.open_correction({
            "subject_type": "contract", "subject_id": record_id, "severity": "minor", "reason": "Clarify wording"
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        with pytest.raises(WorkflowGateError, match="corrections remain open"):
            repo.publish(draft["publication_id"])
        corrected = copy.deepcopy(created["contract"])
        corrected["facts"]["goal"]["statement"] += " and document distributional outcomes."
        repo.apply_contract_correction(correction["correction_id"], corrected, expected_contract_revision=1)
        with pytest.raises(WorkflowGateError, match="content changed"):
            repo.publish(draft["publication_id"])


def test_review_workflow_schema_and_workspace_restore(tmp_path):
    schema = json.loads((ROOT / "schemas/global_impact_review_workflow.schema.json").read_text())
    bundle_schema = json.loads((ROOT / "schemas/global_impact_workspace_bundle.schema.json").read_text())
    source_db, target_db = tmp_path / "source.sqlite3", tmp_path / "target.sqlite3"
    with SQLiteImpactRepository(source_db) as repo:
        _, workspace_id, initiative_id, record_id = create(repo)
        _approve_contract(repo, workspace_id, initiative_id, record_id)
        publication = repo.create_publication({"subject_type": "contract", "subject_id": record_id, "title": "Reviewed brief"}, workspace_id=workspace_id, initiative_id=initiative_id)
        repo.publish(publication["publication_id"], actor="publisher")
        workflow = repo.export_review_workflow(workspace_id)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(workflow)
        bundle = repo.export_workspace_bundle(workspace_id)
        Draft202012Validator(bundle_schema, format_checker=FormatChecker()).validate(bundle)
        assert bundle["bundle_version"] == "1.10.0"
        assert bundle["database_schema_version"] == 11
    with SQLiteImpactRepository(target_db) as restored:
        result = restored.restore_workspace_bundle(bundle)
        assert result["status"] == "restored"
        assert restored.restore_workspace_bundle(bundle)["status"] == "unchanged"
        restored_workflow = restored.export_review_workflow(workspace_id)
        assert restored_workflow["integrity"] == workflow["integrity"]
        assert restored_workflow["publications"][0]["publication_status"] == "published"
        assert restored_workflow["revisions"][0]["content_hash"] == workflow["revisions"][0]["content_hash"]
