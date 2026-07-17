"""Review, quality, revision, correction, and publication workflow.

Global Impact Catalyst v1.6.0 adds governed human review around the existing
canonical contract, evidence, registry, and measurement repositories. Workflow
records are append-oriented and do not rewrite historical decisions or
publication events.
"""
from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Sequence

REVIEW_WORKFLOW_VERSION = "1.6.0"
SUBJECT_TYPES = {
    "contract", "initiative", "evidence_repository", "indicator_registry",
    "measurement_repository", "impact_result", "observation", "publication",
}
ASSIGNMENT_STATUSES = {"pending", "in_review", "changes_requested", "approved", "rejected", "cancelled"}
ASSIGNMENT_PRIORITIES = {"low", "normal", "high", "urgent"}
COMMENT_VISIBILITIES = {"workspace", "reviewers", "private"}
COMMENT_RESOLUTIONS = {"open", "resolved", "wont_fix"}
ASSESSMENT_STATUSES = {"draft", "submitted", "superseded"}
DECISIONS = {"approve", "request_changes", "reject", "abstain"}
CORRECTION_SEVERITIES = {"minor", "material", "critical"}
CORRECTION_STATUSES = {"open", "applied", "rejected", "cancelled"}
PUBLICATION_STATUSES = {"draft", "published", "withdrawn", "superseded"}
CHANGE_TYPES = {"create", "edit", "review_response", "correction", "publish", "withdraw", "restore"}
DEFAULT_QUALITY_THRESHOLD = 60.0

DEFAULT_ROLES = (
    ("program_owner", "Program Owner", ["edit", "submit_review", "respond_review", "open_correction"]),
    ("evidence_reviewer", "Evidence Reviewer", ["review_evidence", "comment", "assess_quality", "request_changes"]),
    ("methods_reviewer", "Methods Reviewer", ["review_methods", "comment", "assess_quality", "request_changes"]),
    ("approver", "Approver", ["comment", "assess_quality", "approve", "reject"]),
    ("publisher", "Publisher", ["publish", "withdraw", "supersede"]),
)


class ReviewWorkflowError(RuntimeError):
    """Base workflow error."""


class WorkflowGateError(ReviewWorkflowError):
    """Raised when a governance gate prevents an action."""


class WorkflowNotFoundError(ReviewWorkflowError):
    """Raised when a workflow record is missing."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def workflow_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def workflow_id(kind: str, *parts: Any) -> str:
    material = "|".join(canonical_json(part) if isinstance(part, (dict, list)) else str(part) for part in parts)
    return f"gic-{kind}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


class ReviewWorkflowMixin:
    """Mixin implemented by the SQLite reference repository."""

    @contextmanager
    def _workflow_transaction(self) -> Iterator[Any]:
        if self.connection.in_transaction:
            yield self.connection
        else:
            with self.transaction() as connection:
                yield connection

    @staticmethod
    def _workflow_decode(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            if field in item:
                raw = item.pop(field)
                item[field.removesuffix("_json")] = json.loads(raw or "{}")
        return item

    def ensure_default_workflow_roles(self, workspace_id: str, *, actor: str = "system") -> List[Dict[str, Any]]:
        roles = []
        for key, name, permissions in DEFAULT_ROLES:
            role_id = workflow_id("role", workspace_id, key)
            existing = self.connection.execute("SELECT * FROM workflow_roles WHERE role_id=?", (role_id,)).fetchone()
            if not existing:
                now = utc_now()
                with self._workflow_transaction():
                    self.connection.execute(
                        """INSERT INTO workflow_roles(role_id,workspace_id,name,description,permissions_json,is_system,
                           archived_at,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (role_id, workspace_id, name, f"System role for {name.lower()} workflow responsibilities.",
                         canonical_json(permissions), 1, None, 1, now, now, canonical_json({"role_key": key})),
                    )
                    self._audit("create_workflow_role", "workflow_role", role_id, workspace_id=workspace_id, revision=1, actor=actor)
            roles.append(self.get_workflow_role(role_id))
        return roles

    def register_workflow_role(
        self, role: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        name = str(role.get("name") or "").strip()
        if not name:
            raise ReviewWorkflowError("workflow role name is required")
        permissions = sorted({str(item).strip() for item in (role.get("permissions") or []) if str(item).strip()})
        role_id = str(role.get("role_id") or role.get("id") or workflow_id("role", workspace_id, name.casefold()))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM workflow_roles WHERE role_id=?", (role_id,)).fetchone()
        with self._workflow_transaction():
            if existing:
                actual = int(existing["revision"])
                if expected_revision is not None and expected_revision != actual:
                    self._registry_concurrency("workflow_role", role_id, int(expected_revision), actual)
                revision = actual + 1
                self.connection.execute(
                    """UPDATE workflow_roles SET name=?,description=?,permissions_json=?,archived_at=?,revision=?,
                       updated_at=?,metadata_json=? WHERE role_id=?""",
                    (name, str(role.get("description") or ""), canonical_json(permissions), role.get("archived_at"),
                     revision, now, canonical_json(role.get("metadata") or {}), role_id),
                )
                action = "update_workflow_role"
            else:
                if expected_revision not in (None, 0):
                    self._registry_concurrency("workflow_role", role_id, int(expected_revision), 0)
                revision = 1
                self.connection.execute(
                    """INSERT INTO workflow_roles(role_id,workspace_id,name,description,permissions_json,is_system,
                       archived_at,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (role_id, workspace_id, name, str(role.get("description") or ""), canonical_json(permissions),
                     int(bool(role.get("is_system"))), role.get("archived_at"), revision,
                     str(role.get("created_at") or now), now, canonical_json(role.get("metadata") or {})),
                )
                action = "create_workflow_role"
            self._audit(action, "workflow_role", role_id, workspace_id=workspace_id, revision=revision, actor=actor)
        return self.get_workflow_role(role_id)

    def get_workflow_role(self, role_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM workflow_roles WHERE role_id=?", (role_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"workflow role not found: {role_id}")
        return self._workflow_decode(row, "permissions_json", "metadata_json")

    def list_workflow_roles(self, workspace_id: str, *, include_archived: bool = False) -> List[Dict[str, Any]]:
        clause = "" if include_archived else " AND archived_at IS NULL"
        rows = self.connection.execute(
            f"SELECT * FROM workflow_roles WHERE workspace_id=?{clause} ORDER BY is_system DESC,name", (workspace_id,)
        ).fetchall()
        return [self._workflow_decode(row, "permissions_json", "metadata_json") for row in rows]

    def create_review_assignment(
        self, assignment: Dict[str, Any], *, workspace_id: str, initiative_id: str,
        actor: str = "system",
    ) -> Dict[str, Any]:
        subject_type = str(assignment.get("subject_type") or "contract")
        if subject_type not in SUBJECT_TYPES:
            raise ReviewWorkflowError(f"unsupported review subject type: {subject_type}")
        subject_id = str(assignment.get("subject_id") or initiative_id).strip()
        reviewer_id = str(assignment.get("reviewer_id") or "").strip()
        role_id = str(assignment.get("role_id") or "").strip()
        if not reviewer_id or not role_id:
            raise ReviewWorkflowError("reviewer_id and role_id are required")
        role = self.get_workflow_role(role_id)
        if role["workspace_id"] != workspace_id or role.get("archived_at"):
            raise ReviewWorkflowError("review role is not active in the requested workspace")
        priority = str(assignment.get("priority") or "normal")
        if priority not in ASSIGNMENT_PRIORITIES:
            raise ReviewWorkflowError(f"unsupported review priority: {priority}")
        now = utc_now()
        assignment_id = str(assignment.get("assignment_id") or assignment.get("id") or workflow_id(
            "review-assignment", workspace_id, initiative_id, subject_type, subject_id, reviewer_id, role_id, now
        ))
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO review_assignments(assignment_id,workspace_id,initiative_id,subject_type,subject_id,
                   reviewer_id,role_id,status,priority,due_at,assigned_by,assigned_at,started_at,completed_at,
                   revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (assignment_id, workspace_id, initiative_id, subject_type, subject_id, reviewer_id, role_id,
                 "pending", priority, assignment.get("due_at"), str(assignment.get("assigned_by") or actor), now,
                 None, None, 1, now, now, canonical_json(assignment.get("metadata") or {})),
            )
            self._audit("create_review_assignment", "review_assignment", assignment_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, revision=1, actor=actor,
                        details={"subject_type": subject_type, "subject_id": subject_id, "reviewer_id": reviewer_id})
        return self.get_review_assignment(assignment_id)

    def get_review_assignment(self, assignment_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM review_assignments WHERE assignment_id=?", (assignment_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"review assignment not found: {assignment_id}")
        item = self._workflow_decode(row, "metadata_json")
        item["comments"] = self.list_review_comments(assignment_id=assignment_id)
        item["quality_assessments"] = self.list_quality_assessments(assignment_id=assignment_id)
        item["decisions"] = self.list_approval_decisions(assignment_id=assignment_id)
        return item

    def list_review_assignments(
        self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None,
        reviewer_id: Optional[str] = None, status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("workspace_id", workspace_id), ("initiative_id", initiative_id),
                             ("reviewer_id", reviewer_id), ("status", status)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM review_assignments WHERE {' AND '.join(clauses)} ORDER BY assigned_at,assignment_id", params
        ).fetchall()
        return [self._workflow_decode(row, "metadata_json") for row in rows]

    def update_review_assignment_status(
        self, assignment_id: str, status: str, *, expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        if status not in ASSIGNMENT_STATUSES:
            raise ReviewWorkflowError(f"unsupported assignment status: {status}")
        current = self.get_review_assignment(assignment_id)
        actual = int(current["revision"])
        if expected_revision is not None and expected_revision != actual:
            self._registry_concurrency("review_assignment", assignment_id, int(expected_revision), actual)
        now = utc_now()
        started_at = current.get("started_at") or (now if status == "in_review" else None)
        completed_at = now if status in {"approved", "rejected", "cancelled"} else None
        with self._workflow_transaction():
            self.connection.execute(
                "UPDATE review_assignments SET status=?,started_at=?,completed_at=?,revision=?,updated_at=? WHERE assignment_id=?",
                (status, started_at, completed_at, actual + 1, now, assignment_id),
            )
            self._audit("update_review_status", "review_assignment", assignment_id,
                        workspace_id=current["workspace_id"], initiative_id=current["initiative_id"],
                        revision=actual + 1, actor=actor, details={"status": status})
        return self.get_review_assignment(assignment_id)

    def add_review_comment(
        self, assignment_id: str, comment: Dict[str, Any], *, actor: str = "system",
    ) -> Dict[str, Any]:
        assignment = self.get_review_assignment(assignment_id)
        body = str(comment.get("body") or "").strip()
        if not body:
            raise ReviewWorkflowError("review comment body is required")
        visibility = str(comment.get("visibility") or "workspace")
        if visibility not in COMMENT_VISIBILITIES:
            raise ReviewWorkflowError(f"unsupported comment visibility: {visibility}")
        parent = comment.get("parent_comment_id")
        if parent:
            parent_row = self.connection.execute("SELECT assignment_id FROM review_comments WHERE comment_id=?", (parent,)).fetchone()
            if not parent_row or parent_row["assignment_id"] != assignment_id:
                raise ReviewWorkflowError("parent comment must belong to the same assignment")
        now = utc_now()
        author_id = str(comment.get("author_id") or actor)
        comment_id = str(comment.get("comment_id") or comment.get("id") or workflow_id(
            "review-comment", assignment_id, author_id, now, body
        ))
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO review_comments(comment_id,assignment_id,workspace_id,initiative_id,subject_type,
                   subject_id,author_id,parent_comment_id,visibility,body,resolution_status,resolved_by,resolved_at,
                   revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (comment_id, assignment_id, assignment["workspace_id"], assignment["initiative_id"],
                 assignment["subject_type"], assignment["subject_id"], author_id, parent, visibility, body,
                 "open", None, None, 1, now, now, canonical_json(comment.get("metadata") or {})),
            )
            self._audit("add_review_comment", "review_comment", comment_id,
                        workspace_id=assignment["workspace_id"], initiative_id=assignment["initiative_id"],
                        revision=1, actor=actor, details={"assignment_id": assignment_id})
        return self.get_review_comment(comment_id)

    def get_review_comment(self, comment_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM review_comments WHERE comment_id=?", (comment_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"review comment not found: {comment_id}")
        return self._workflow_decode(row, "metadata_json")

    def list_review_comments(
        self, *, assignment_id: Optional[str] = None, subject_type: Optional[str] = None,
        subject_id: Optional[str] = None, resolution_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("assignment_id", assignment_id), ("subject_type", subject_type),
                             ("subject_id", subject_id), ("resolution_status", resolution_status)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM review_comments WHERE {' AND '.join(clauses)} ORDER BY created_at,comment_id", params
        ).fetchall()
        return [self._workflow_decode(row, "metadata_json") for row in rows]

    def resolve_review_comment(
        self, comment_id: str, *, resolution_status: str = "resolved", expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        if resolution_status not in COMMENT_RESOLUTIONS - {"open"}:
            raise ReviewWorkflowError("resolution_status must be resolved or wont_fix")
        current = self.get_review_comment(comment_id)
        actual = int(current["revision"])
        if expected_revision is not None and expected_revision != actual:
            self._registry_concurrency("review_comment", comment_id, int(expected_revision), actual)
        now = utc_now()
        with self._workflow_transaction():
            self.connection.execute(
                "UPDATE review_comments SET resolution_status=?,resolved_by=?,resolved_at=?,revision=?,updated_at=? WHERE comment_id=?",
                (resolution_status, actor, now, actual + 1, now, comment_id),
            )
            self._audit("resolve_review_comment", "review_comment", comment_id,
                        workspace_id=current["workspace_id"], initiative_id=current["initiative_id"],
                        revision=actual + 1, actor=actor, details={"resolution_status": resolution_status})
        return self.get_review_comment(comment_id)

    @staticmethod
    def _quality_score(dimensions: Sequence[Dict[str, Any]]) -> tuple[float, float, str, List[Dict[str, Any]]]:
        if not dimensions:
            raise ReviewWorkflowError("at least one quality dimension is required")
        clean = []
        weighted_score = 0.0
        weighted_max = 0.0
        for item in dimensions:
            key = str(item.get("key") or item.get("name") or "").strip()
            score = float(item.get("score", 0))
            maximum = float(item.get("maximum_score", item.get("max_score", 100)))
            weight = float(item.get("weight", 1))
            if not key or maximum <= 0 or weight <= 0 or score < 0 or score > maximum:
                raise ReviewWorkflowError("quality dimensions require a key and bounded positive scores")
            weighted_score += score * weight
            weighted_max += maximum * weight
            clean.append({"key": key, "score": score, "maximum_score": maximum, "weight": weight,
                          "finding": str(item.get("finding") or "")})
        percentage = round((weighted_score / weighted_max) * 100, 2)
        grade = "excellent" if percentage >= 90 else "strong" if percentage >= 75 else "adequate" if percentage >= 60 else "weak"
        return percentage, 100.0, grade, clean

    def submit_quality_assessment(
        self, assessment: Dict[str, Any], *, workspace_id: str, initiative_id: str,
        assignment_id: Optional[str] = None, actor: str = "system",
    ) -> Dict[str, Any]:
        subject_type = str(assessment.get("subject_type") or "contract")
        subject_id = str(assessment.get("subject_id") or initiative_id)
        if subject_type not in SUBJECT_TYPES:
            raise ReviewWorkflowError(f"unsupported quality subject type: {subject_type}")
        if assignment_id:
            assignment = self.get_review_assignment(assignment_id)
            if assignment["workspace_id"] != workspace_id or assignment["initiative_id"] != initiative_id:
                raise ReviewWorkflowError("quality assessment assignment scope mismatch")
            subject_type, subject_id = assignment["subject_type"], assignment["subject_id"]
        score, maximum, grade, dimensions = self._quality_score(assessment.get("dimensions") or [])
        status = str(assessment.get("status") or "submitted")
        if status not in ASSESSMENT_STATUSES:
            raise ReviewWorkflowError(f"unsupported assessment status: {status}")
        assessor_id = str(assessment.get("assessor_id") or actor)
        now = utc_now()
        assessment_id = str(assessment.get("assessment_id") or assessment.get("id") or workflow_id(
            "quality-assessment", workspace_id, initiative_id, subject_type, subject_id, assessor_id, now
        ))
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO quality_assessments(assessment_id,assignment_id,workspace_id,initiative_id,
                   subject_type,subject_id,rubric_id,rubric_version,assessor_id,status,score,maximum_score,grade,
                   dimensions_json,findings_json,limitations,revision,created_at,updated_at,submitted_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (assessment_id, assignment_id, workspace_id, initiative_id, subject_type, subject_id,
                 str(assessment.get("rubric_id") or "gic-core-quality"),
                 str(assessment.get("rubric_version") or "1.0"), assessor_id, status, score, maximum, grade,
                 canonical_json(dimensions), canonical_json(assessment.get("findings") or []),
                 str(assessment.get("limitations") or ""), 1, now, now, now if status == "submitted" else None,
                 canonical_json(assessment.get("metadata") or {})),
            )
            self._audit("submit_quality_assessment", "quality_assessment", assessment_id,
                        workspace_id=workspace_id, initiative_id=initiative_id, revision=1, actor=actor,
                        details={"score": score, "grade": grade, "subject_type": subject_type, "subject_id": subject_id})
        return self.get_quality_assessment(assessment_id)

    def get_quality_assessment(self, assessment_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM quality_assessments WHERE assessment_id=?", (assessment_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"quality assessment not found: {assessment_id}")
        return self._workflow_decode(row, "dimensions_json", "findings_json", "metadata_json")

    def list_quality_assessments(
        self, *, assignment_id: Optional[str] = None, subject_type: Optional[str] = None,
        subject_id: Optional[str] = None, status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("assignment_id", assignment_id), ("subject_type", subject_type),
                             ("subject_id", subject_id), ("status", status)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM quality_assessments WHERE {' AND '.join(clauses)} ORDER BY created_at,assessment_id", params
        ).fetchall()
        return [self._workflow_decode(row, "dimensions_json", "findings_json", "metadata_json") for row in rows]

    def record_approval_decision(
        self, assignment_id: str, decision: str, *, rationale: str, conditions: Optional[List[Any]] = None,
        reviewer_id: Optional[str] = None, actor: str = "system",
    ) -> Dict[str, Any]:
        if decision not in DECISIONS:
            raise ReviewWorkflowError(f"unsupported approval decision: {decision}")
        assignment = self.get_review_assignment(assignment_id)
        reviewer = str(reviewer_id or actor)
        if reviewer != assignment["reviewer_id"] and actor != "system":
            raise WorkflowGateError("only the assigned reviewer may record this decision")
        if decision == "approve":
            unresolved = self.list_review_comments(assignment_id=assignment_id, resolution_status="open")
            if unresolved:
                raise WorkflowGateError("approval is blocked while review comments remain open")
            assessments = self.list_quality_assessments(assignment_id=assignment_id, status="submitted")
            if not assessments:
                raise WorkflowGateError("approval requires a submitted quality assessment")
            if assessments[-1]["score"] < DEFAULT_QUALITY_THRESHOLD:
                raise WorkflowGateError("approval requires an adequate quality score")
        now = utc_now()
        prior = self.list_approval_decisions(assignment_id=assignment_id)
        decision_id = workflow_id("approval-decision", assignment_id, reviewer, decision, now)
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO approval_decisions(decision_id,assignment_id,workspace_id,initiative_id,subject_type,
                   subject_id,reviewer_id,decision,rationale,conditions_json,decided_at,supersedes_decision_id,
                   revision,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (decision_id, assignment_id, assignment["workspace_id"], assignment["initiative_id"],
                 assignment["subject_type"], assignment["subject_id"], reviewer, decision, rationale.strip(),
                 canonical_json(conditions or []), now, prior[-1]["decision_id"] if prior else None, 1,
                 canonical_json({})),
            )
            status = {"approve": "approved", "request_changes": "changes_requested", "reject": "rejected", "abstain": "in_review"}[decision]
            current_revision = int(assignment["revision"])
            self.connection.execute(
                "UPDATE review_assignments SET status=?,completed_at=?,revision=?,updated_at=? WHERE assignment_id=?",
                (status, now if status in {"approved", "rejected"} else None, current_revision + 1, now, assignment_id),
            )
            self._audit("record_approval_decision", "approval_decision", decision_id,
                        workspace_id=assignment["workspace_id"], initiative_id=assignment["initiative_id"],
                        revision=1, actor=actor, details={"decision": decision, "assignment_id": assignment_id})
        return self.get_approval_decision(decision_id)

    def get_approval_decision(self, decision_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM approval_decisions WHERE decision_id=?", (decision_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"approval decision not found: {decision_id}")
        return self._workflow_decode(row, "conditions_json", "metadata_json")

    def list_approval_decisions(
        self, *, assignment_id: Optional[str] = None, subject_type: Optional[str] = None,
        subject_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("assignment_id", assignment_id), ("subject_type", subject_type), ("subject_id", subject_id)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM approval_decisions WHERE {' AND '.join(clauses)} ORDER BY decided_at,decision_id", params
        ).fetchall()
        return [self._workflow_decode(row, "conditions_json", "metadata_json") for row in rows]

    def record_workflow_revision(
        self, *, workspace_id: str, initiative_id: str, subject_type: str, subject_id: str,
        snapshot: Dict[str, Any], change_type: str = "edit", actor: str = "system", summary: str = "",
        previous_content_hash: Optional[str] = None, revision_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if subject_type not in SUBJECT_TYPES:
            raise ReviewWorkflowError(f"unsupported revision subject type: {subject_type}")
        if change_type not in CHANGE_TYPES:
            raise ReviewWorkflowError(f"unsupported revision change type: {change_type}")
        digest = workflow_hash(snapshot)
        existing = self.connection.execute(
            "SELECT * FROM workflow_revisions WHERE subject_type=? AND subject_id=? AND content_hash=?",
            (subject_type, subject_id, digest),
        ).fetchone()
        if existing:
            return self._workflow_decode(existing, "snapshot_json", "metadata_json")
        if revision_number is None:
            row = self.connection.execute(
                "SELECT COALESCE(MAX(revision_number),0)+1 AS revision_number FROM workflow_revisions WHERE subject_type=? AND subject_id=?",
                (subject_type, subject_id),
            ).fetchone()
            revision_number = int(row["revision_number"])
        revision_id = workflow_id("workflow-revision", subject_type, subject_id, revision_number, digest)
        now = utc_now()
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO workflow_revisions(workflow_revision_id,workspace_id,initiative_id,subject_type,
                   subject_id,revision_number,change_type,actor_id,summary,previous_content_hash,content_hash,
                   snapshot_json,created_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (revision_id, workspace_id, initiative_id, subject_type, subject_id, revision_number, change_type,
                 actor, summary or f"{change_type.replace('_', ' ').title()} revision {revision_number}",
                 previous_content_hash, digest, canonical_json(snapshot), now, canonical_json(metadata or {})),
            )
            self._audit("record_workflow_revision", "workflow_revision", revision_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, revision=revision_number, actor=actor,
                        details={"subject_type": subject_type, "subject_id": subject_id, "content_hash": digest})
        return self.get_workflow_revision(revision_id)

    def get_workflow_revision(self, revision_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM workflow_revisions WHERE workflow_revision_id=?", (revision_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"workflow revision not found: {revision_id}")
        return self._workflow_decode(row, "snapshot_json", "metadata_json")

    def list_workflow_revisions(self, subject_type: str, subject_id: str) -> List[Dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT * FROM workflow_revisions WHERE subject_type=? AND subject_id=? ORDER BY revision_number",
            (subject_type, subject_id),
        ).fetchall()
        return [self._workflow_decode(row, "snapshot_json", "metadata_json") for row in rows]

    def open_correction(
        self, correction: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system",
    ) -> Dict[str, Any]:
        subject_type = str(correction.get("subject_type") or "contract")
        subject_id = str(correction.get("subject_id") or initiative_id)
        severity = str(correction.get("severity") or "minor")
        if subject_type not in SUBJECT_TYPES or severity not in CORRECTION_SEVERITIES:
            raise ReviewWorkflowError("unsupported correction subject or severity")
        reason = str(correction.get("reason") or "").strip()
        if not reason:
            raise ReviewWorkflowError("correction reason is required")
        now = utc_now()
        correction_id = str(correction.get("correction_id") or workflow_id(
            "correction", workspace_id, initiative_id, subject_type, subject_id, now, reason
        ))
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO correction_records(correction_id,workspace_id,initiative_id,subject_type,subject_id,
                   severity,status,reason,proposed_changes_json,opened_by,opened_at,applied_by,applied_at,
                   resulting_revision_id,resolution_notes,revision,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (correction_id, workspace_id, initiative_id, subject_type, subject_id, severity, "open", reason,
                 canonical_json(correction.get("proposed_changes") or {}), str(correction.get("opened_by") or actor),
                 now, None, None, None, "", 1, now, canonical_json(correction.get("metadata") or {})),
            )
            self._audit("open_correction", "correction", correction_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, revision=1, actor=actor,
                        details={"subject_type": subject_type, "subject_id": subject_id, "severity": severity})
        return self.get_correction(correction_id)

    def get_correction(self, correction_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM correction_records WHERE correction_id=?", (correction_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"correction not found: {correction_id}")
        return self._workflow_decode(row, "proposed_changes_json", "metadata_json")

    def list_corrections(
        self, *, workspace_id: Optional[str] = None, subject_type: Optional[str] = None,
        subject_id: Optional[str] = None, status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("workspace_id", workspace_id), ("subject_type", subject_type),
                             ("subject_id", subject_id), ("status", status)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM correction_records WHERE {' AND '.join(clauses)} ORDER BY opened_at,correction_id", params
        ).fetchall()
        return [self._workflow_decode(row, "proposed_changes_json", "metadata_json") for row in rows]

    def apply_contract_correction(
        self, correction_id: str, corrected_contract: Dict[str, Any], *, expected_contract_revision: int,
        actor: str = "system", resolution_notes: str = "",
    ) -> Dict[str, Any]:
        correction = self.get_correction(correction_id)
        if correction["status"] != "open" or correction["subject_type"] != "contract":
            raise WorkflowGateError("only open contract corrections can be applied through this method")
        stored = self.save_contract(corrected_contract, expected_revision=expected_contract_revision, actor=actor)
        revisions = self.list_workflow_revisions("contract", stored["record_id"])
        resulting = revisions[-1]
        now = utc_now()
        with self._workflow_transaction():
            self.connection.execute(
                """UPDATE correction_records SET status='applied',applied_by=?,applied_at=?,resulting_revision_id=?,
                   resolution_notes=?,revision=revision+1,updated_at=? WHERE correction_id=?""",
                (actor, now, resulting["workflow_revision_id"], resolution_notes, now, correction_id),
            )
            self._audit("apply_correction", "correction", correction_id,
                        workspace_id=correction["workspace_id"], initiative_id=correction["initiative_id"],
                        revision=int(correction["revision"]) + 1, actor=actor,
                        details={"resulting_revision_id": resulting["workflow_revision_id"]})
        return {"correction": self.get_correction(correction_id), "contract": stored, "revision": resulting}

    def _subject_snapshot(self, subject_type: str, subject_id: str, workspace_id: str, initiative_id: str) -> Dict[str, Any]:
        if subject_type == "contract":
            try:
                return self.get_contract(record_id=subject_id)["contract"]
            except Exception:
                return self.get_contract(initiative_id=initiative_id)["contract"]
        if subject_type == "initiative":
            return self.get_entity("initiative", subject_id, include_archived=True)["document"]
        if subject_type == "evidence_repository":
            return self.export_evidence_repository(workspace_id)
        if subject_type == "indicator_registry":
            return self.export_indicator_registry(workspace_id)
        if subject_type == "measurement_repository":
            return self.export_measurement_repository(workspace_id)
        if subject_type == "impact_result":
            return self.get_impact_result(subject_id)
        if subject_type == "observation":
            return self.get_observation(subject_id)
        raise ReviewWorkflowError(f"cannot resolve snapshot for subject type: {subject_type}")

    def create_publication(
        self, publication: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system",
    ) -> Dict[str, Any]:
        subject_type = str(publication.get("subject_type") or "contract")
        subject_id = str(publication.get("subject_id") or initiative_id)
        if subject_type not in SUBJECT_TYPES - {"publication"}:
            raise ReviewWorkflowError(f"unsupported publication subject: {subject_type}")
        title = str(publication.get("title") or "").strip()
        if not title:
            raise ReviewWorkflowError("publication title is required")
        snapshot = self._subject_snapshot(subject_type, subject_id, workspace_id, initiative_id)
        digest = workflow_hash(snapshot)
        now = utc_now()
        publication_id = str(publication.get("publication_id") or workflow_id(
            "publication", workspace_id, initiative_id, subject_type, subject_id, title, now
        ))
        with self._workflow_transaction():
            self.connection.execute(
                """INSERT INTO publication_records(publication_id,workspace_id,initiative_id,subject_type,subject_id,
                   title,publication_status,release_label,public_url,approved_decision_id,quality_assessment_id,
                   content_hash,published_revision_id,published_at,published_by,withdrawn_at,withdrawn_by,
                   withdrawal_reason,supersedes_publication_id,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (publication_id, workspace_id, initiative_id, subject_type, subject_id, title, "draft",
                 str(publication.get("release_label") or ""), str(publication.get("public_url") or ""), None, None,
                 digest, None, None, None, None, None, "", publication.get("supersedes_publication_id"), 1,
                 now, now, canonical_json(publication.get("metadata") or {})),
            )
            self._publication_event(publication_id, "created", actor, details={"content_hash": digest})
            self._audit("create_publication", "publication", publication_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, revision=1, actor=actor,
                        details={"subject_type": subject_type, "subject_id": subject_id})
        return self.get_publication(publication_id)

    def _publication_event(self, publication_id: str, event_type: str, actor: str, *, reason: str = "", details: Optional[Dict[str, Any]] = None) -> None:
        now = utc_now()
        event_id = workflow_id("publication-event", publication_id, event_type, now, reason)
        self.connection.execute(
            "INSERT INTO publication_events(publication_event_id,publication_id,event_type,actor_id,reason,event_at,details_json) VALUES (?,?,?,?,?,?,?)",
            (event_id, publication_id, event_type, actor, reason, now, canonical_json(details or {})),
        )

    def get_publication(self, publication_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM publication_records WHERE publication_id=?", (publication_id,)).fetchone()
        if not row:
            raise WorkflowNotFoundError(f"publication not found: {publication_id}")
        item = self._workflow_decode(row, "metadata_json")
        events = self.connection.execute(
            "SELECT * FROM publication_events WHERE publication_id=? ORDER BY event_at,publication_event_id", (publication_id,)
        ).fetchall()
        item["events"] = [self._workflow_decode(event, "details_json") for event in events]
        return item

    def list_publications(
        self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None,
        publication_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("workspace_id", workspace_id), ("initiative_id", initiative_id),
                             ("publication_status", publication_status)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM publication_records WHERE {' AND '.join(clauses)} ORDER BY created_at,publication_id", params
        ).fetchall()
        return [self._workflow_decode(row, "metadata_json") for row in rows]

    def publish(
        self, publication_id: str, *, actor: str = "system", quality_threshold: float = DEFAULT_QUALITY_THRESHOLD,
    ) -> Dict[str, Any]:
        publication = self.get_publication(publication_id)
        if publication["publication_status"] != "draft":
            raise WorkflowGateError("only draft publications can be published")
        subject_type, subject_id = publication["subject_type"], publication["subject_id"]
        decisions = [item for item in self.list_approval_decisions(subject_type=subject_type, subject_id=subject_id) if item["decision"] == "approve"]
        if not decisions:
            raise WorkflowGateError("publication requires an approval decision")
        assessments = [item for item in self.list_quality_assessments(subject_type=subject_type, subject_id=subject_id, status="submitted") if float(item["score"]) >= quality_threshold]
        if not assessments:
            raise WorkflowGateError("publication requires an adequate submitted quality assessment")
        open_corrections = self.list_corrections(subject_type=subject_type, subject_id=subject_id, status="open")
        if open_corrections:
            raise WorkflowGateError("publication is blocked while corrections remain open")
        snapshot = self._subject_snapshot(subject_type, subject_id, publication["workspace_id"], publication["initiative_id"])
        digest = workflow_hash(snapshot)
        if digest != publication["content_hash"]:
            raise WorkflowGateError("publication content changed after the draft was created; create a new draft")
        revision = self.record_workflow_revision(
            workspace_id=publication["workspace_id"], initiative_id=publication["initiative_id"],
            subject_type=subject_type, subject_id=subject_id, snapshot=snapshot, change_type="publish", actor=actor,
            summary=f"Published as {publication['title']}",
        )
        now = utc_now()
        with self._workflow_transaction():
            self.connection.execute(
                """UPDATE publication_records SET publication_status='published',approved_decision_id=?,
                   quality_assessment_id=?,published_revision_id=?,published_at=?,published_by=?,revision=revision+1,
                   updated_at=? WHERE publication_id=?""",
                (decisions[-1]["decision_id"], assessments[-1]["assessment_id"], revision["workflow_revision_id"],
                 now, actor, now, publication_id),
            )
            self._publication_event(publication_id, "published", actor,
                                    details={"decision_id": decisions[-1]["decision_id"], "assessment_id": assessments[-1]["assessment_id"]})
            self._audit("publish", "publication", publication_id, workspace_id=publication["workspace_id"],
                        initiative_id=publication["initiative_id"], revision=int(publication["revision"]) + 1,
                        actor=actor, details={"workflow_revision_id": revision["workflow_revision_id"]})
        return self.get_publication(publication_id)

    def withdraw_publication(self, publication_id: str, *, reason: str, actor: str = "system") -> Dict[str, Any]:
        publication = self.get_publication(publication_id)
        if publication["publication_status"] != "published":
            raise WorkflowGateError("only published records can be withdrawn")
        if not reason.strip():
            raise ReviewWorkflowError("withdrawal reason is required")
        now = utc_now()
        with self._workflow_transaction():
            self.connection.execute(
                """UPDATE publication_records SET publication_status='withdrawn',withdrawn_at=?,withdrawn_by=?,
                   withdrawal_reason=?,revision=revision+1,updated_at=? WHERE publication_id=?""",
                (now, actor, reason.strip(), now, publication_id),
            )
            self._publication_event(publication_id, "withdrawn", actor, reason=reason.strip())
            self._audit("withdraw_publication", "publication", publication_id,
                        workspace_id=publication["workspace_id"], initiative_id=publication["initiative_id"],
                        revision=int(publication["revision"]) + 1, actor=actor, details={"reason": reason.strip()})
        return self.get_publication(publication_id)

    def _materialize_contract_workflow(
        self, contract: Dict[str, Any], *, repository_revision: int, previous_content_hash: Optional[str],
        action: str, actor: str = "system",
    ) -> None:
        workspace_id = contract["facts"]["workspace"]["id"]
        initiative_id = contract["facts"]["initiative"]["id"]
        self.ensure_default_workflow_roles(workspace_id, actor=actor)
        self.record_workflow_revision(
            workspace_id=workspace_id, initiative_id=initiative_id, subject_type="contract",
            subject_id=contract["record_id"], snapshot=contract,
            change_type="create" if repository_revision == 1 else "edit",
            actor=actor, summary=f"Canonical contract repository revision {repository_revision}",
            previous_content_hash=previous_content_hash, revision_number=repository_revision,
            metadata={"repository_action": action, "contract_version": contract.get("contract_version")},
        )

    def export_review_workflow(self, workspace_id: str) -> Dict[str, Any]:
        roles = self.list_workflow_roles(workspace_id, include_archived=True)
        assignments = self.list_review_assignments(workspace_id=workspace_id)
        comments = [self._workflow_decode(row, "metadata_json") for row in self.connection.execute(
            "SELECT * FROM review_comments WHERE workspace_id=? ORDER BY created_at,comment_id", (workspace_id,)
        ).fetchall()]
        assessments = [self._workflow_decode(row, "dimensions_json", "findings_json", "metadata_json") for row in self.connection.execute(
            "SELECT * FROM quality_assessments WHERE workspace_id=? ORDER BY created_at,assessment_id", (workspace_id,)
        ).fetchall()]
        decisions = [self._workflow_decode(row, "conditions_json", "metadata_json") for row in self.connection.execute(
            "SELECT * FROM approval_decisions WHERE workspace_id=? ORDER BY decided_at,decision_id", (workspace_id,)
        ).fetchall()]
        revisions = [self._workflow_decode(row, "snapshot_json", "metadata_json") for row in self.connection.execute(
            "SELECT * FROM workflow_revisions WHERE workspace_id=? ORDER BY created_at,workflow_revision_id", (workspace_id,)
        ).fetchall()]
        corrections = self.list_corrections(workspace_id=workspace_id)
        publications = self.list_publications(workspace_id=workspace_id)
        publication_events = [self._workflow_decode(row, "details_json") for row in self.connection.execute(
            """SELECT e.* FROM publication_events e JOIN publication_records p ON p.publication_id=e.publication_id
               WHERE p.workspace_id=? ORDER BY e.event_at,e.publication_event_id""", (workspace_id,)
        ).fetchall()]
        open_comments = [item["comment_id"] for item in comments if item["resolution_status"] == "open"]
        open_corrections = [item["correction_id"] for item in corrections if item["status"] == "open"]
        broken_decisions = [item["decision_id"] for item in decisions if not any(a["assignment_id"] == item["assignment_id"] for a in assignments)]
        published_without_gate = [item["publication_id"] for item in publications if item["publication_status"] == "published" and (not item.get("approved_decision_id") or not item.get("quality_assessment_id"))]
        return {
            "workflow_type": "global_impact_review_workflow",
            "workflow_version": REVIEW_WORKFLOW_VERSION,
            "workspace_id": workspace_id,
            "generated_at": utc_now(),
            "roles": roles,
            "review_assignments": assignments,
            "review_comments": comments,
            "quality_assessments": assessments,
            "approval_decisions": decisions,
            "revisions": revisions,
            "corrections": corrections,
            "publications": publications,
            "publication_events": publication_events,
            "integrity": {
                "valid": not broken_decisions and not published_without_gate,
                "role_count": len(roles), "assignment_count": len(assignments), "comment_count": len(comments),
                "open_comment_count": len(open_comments), "quality_assessment_count": len(assessments),
                "approval_decision_count": len(decisions), "revision_count": len(revisions),
                "correction_count": len(corrections), "open_correction_count": len(open_corrections),
                "publication_count": len(publications), "broken_decision_ids": broken_decisions,
                "published_without_gate_ids": published_without_gate,
            },
            "boundary": "Workflow approval documents governance decisions; it is not external assurance, certification, or a guarantee that source claims are true.",
        }

    def _restore_review_workflow(self, workflow: Dict[str, Any], *, actor: str = "restore") -> None:
        if not workflow:
            return
        workspace_id = workflow["workspace_id"]
        # Restore append-oriented tables directly so historical IDs, timestamps, and revisions remain stable.
        table_specs = (
            ("workflow_roles", workflow.get("roles", []), ("permissions", "metadata")),
            ("review_assignments", workflow.get("review_assignments", []), ("metadata",)),
            ("review_comments", workflow.get("review_comments", []), ("metadata",)),
            ("quality_assessments", workflow.get("quality_assessments", []), ("dimensions", "findings", "metadata")),
            ("approval_decisions", workflow.get("approval_decisions", []), ("conditions", "metadata")),
            ("workflow_revisions", workflow.get("revisions", []), ("snapshot", "metadata")),
            ("correction_records", workflow.get("corrections", []), ("proposed_changes", "metadata")),
            ("publication_records", workflow.get("publications", []), ("metadata",)),
            ("publication_events", workflow.get("publication_events", []), ("details",)),
        )
        for table, items, json_fields in table_specs:
            for item in items:
                values = dict(item)
                for field in json_fields:
                    if field in values:
                        values[f"{field}_json"] = canonical_json(values.pop(field))
                values.pop("events", None)
                columns = list(values)
                self.connection.execute(
                    f"INSERT OR REPLACE INTO {table}({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                    [values[column] for column in columns],
                )
        self.connection.commit()
