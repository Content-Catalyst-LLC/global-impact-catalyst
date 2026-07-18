"""Connected public-interest impact intelligence platform for Global Impact Catalyst v2.0.0.

The platform layer connects governed v1.x repositories without replacing their
contracts. Institutional access, workflows, connections, pathways, and snapshots
remain checksum-bound to the underlying evidence and publication state.
"""
from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional

PLATFORM_VERSION = "2.0.0"
PLATFORM_ROLES = {"owner", "administrator", "researcher", "reviewer", "publisher", "viewer", "integration_service"}
WORKFLOW_TYPES = {"evidence_to_decision", "measurement_to_publication", "publication_to_handoff", "readiness_review", "custom"}
WORKFLOW_STEP_TYPES = {"repository_integrity", "create_snapshot", "release_readiness", "platform_handoff", "emit_event"}
CONNECTION_TYPES = {"internal_module", "public_api", "institutional_api", "file_exchange", "manual_handoff"}
PLATFORM_BOUNDARY = (
    "The connected platform coordinates governed evidence and workflows. It does not certify impact, "
    "prove causation, replace institutional review, or grant access beyond recorded permissions."
)

class PlatformError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    raw = value if isinstance(value, (bytes, bytearray)) else _canonical(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _id(kind: str, *parts: Any) -> str:
    return f"gic-{kind}-{hashlib.sha256('|'.join(str(p) for p in parts).encode()).hexdigest()[:20]}"


class ConnectedImpactPlatformMixin:
    @contextmanager
    def _platform_transaction(self) -> Iterator[Any]:
        nested = bool(self.connection.in_transaction)
        name = "gic_platform_nested"
        try:
            if nested:
                self.connection.execute(f"SAVEPOINT {name}")
            else:
                self.connection.execute("BEGIN IMMEDIATE")
            yield self.connection
        except Exception:
            if nested:
                self.connection.execute(f"ROLLBACK TO SAVEPOINT {name}")
                self.connection.execute(f"RELEASE SAVEPOINT {name}")
            else:
                self.connection.rollback()
            raise
        else:
            if nested:
                self.connection.execute(f"RELEASE SAVEPOINT {name}")
            else:
                self.connection.commit()

    @staticmethod
    def _decode_platform(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            key = field if field.endswith("_json") else f"{field}_json"
            if key in item:
                item[field.removesuffix("_json")] = json.loads(item.pop(key) or "{}")
        return item

    def register_institution(self, institution: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        name = str(institution.get("name") or "").strip()
        if not name:
            raise PlatformError("institution name is required")
        slug = str(institution.get("slug") or "-").strip().lower()
        slug = "-".join(part for part in "".join(c if c.isalnum() else " " for c in slug).split() if part)
        if not slug:
            slug = _hash(name)[:12]
        institution_id = str(institution.get("institution_id") or _id("institution", slug))
        now = _now()
        existing = self.connection.execute("SELECT created_at FROM institutions WHERE institution_id=?", (institution_id,)).fetchone()
        with self._platform_transaction():
            self.connection.execute(
                """INSERT INTO institutions(institution_id,name,slug,mission,governance_model,status,created_at,updated_at,metadata_json)
                VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(institution_id) DO UPDATE SET name=excluded.name,slug=excluded.slug,
                mission=excluded.mission,governance_model=excluded.governance_model,status=excluded.status,
                updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (institution_id, name, slug, str(institution.get("mission") or ""),
                 str(institution.get("governance_model") or "public_interest"), str(institution.get("status") or "active"),
                 existing["created_at"] if existing else now, now, _canonical(institution.get("metadata") or {})),
            )
            self._audit("register", "institution", institution_id, actor=actor, details={"slug": slug})
        return self.get_institution(institution_id)

    def get_institution(self, institution_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM institutions WHERE institution_id=?", (institution_id,)).fetchone()
        if not row:
            raise PlatformError(f"institution not found: {institution_id}")
        return self._decode_platform(row, "metadata")

    def add_institution_member(self, institution_id: str, member: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        self.get_institution(institution_id)
        principal_id = str(member.get("principal_id") or "").strip()
        role = str(member.get("role") or "viewer")
        if not principal_id:
            raise PlatformError("principal_id is required")
        if role not in PLATFORM_ROLES:
            raise PlatformError(f"unsupported platform role: {role}")
        permissions = sorted(set(str(p) for p in (member.get("permissions") or [])))
        membership_id = str(member.get("membership_id") or _id("membership", institution_id, principal_id))
        email = str(member.get("email") or "").strip().lower()
        now = _now()
        with self._platform_transaction():
            self.connection.execute(
                """INSERT INTO institution_members(membership_id,institution_id,principal_id,display_name,email_hash,role,status,
                permissions_json,joined_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(institution_id,principal_id) DO UPDATE SET display_name=excluded.display_name,email_hash=excluded.email_hash,
                role=excluded.role,status=excluded.status,permissions_json=excluded.permissions_json,updated_at=excluded.updated_at,
                metadata_json=excluded.metadata_json""",
                (membership_id, institution_id, principal_id, str(member.get("display_name") or principal_id),
                 hashlib.sha256(email.encode()).hexdigest() if email else None, role, str(member.get("status") or "active"),
                 _canonical(permissions), now, now, _canonical(member.get("metadata") or {})),
            )
            self._audit("add_member", "institution_member", membership_id, actor=actor, details={"institution_id": institution_id, "role": role})
        row = self.connection.execute("SELECT * FROM institution_members WHERE institution_id=? AND principal_id=?", (institution_id, principal_id)).fetchone()
        return self._decode_platform(row, "permissions", "metadata")

    def link_institution_workspace(self, institution_id: str, workspace_id: str, *, relationship: str = "owned", policy: Optional[Dict[str, Any]] = None, actor: str = "system") -> Dict[str, Any]:
        self.get_institution(institution_id)
        self.get_entity("workspace", workspace_id, include_archived=True)
        if relationship not in {"owned", "managed", "partner", "observed"}:
            raise PlatformError(f"unsupported workspace relationship: {relationship}")
        link_id = _id("workspace-link", institution_id, workspace_id)
        now = _now()
        with self._platform_transaction():
            self.connection.execute(
                """INSERT INTO institution_workspaces(link_id,institution_id,workspace_id,relationship,status,policy_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(institution_id,workspace_id) DO UPDATE SET relationship=excluded.relationship,
                status=excluded.status,policy_json=excluded.policy_json,updated_at=excluded.updated_at""",
                (link_id, institution_id, workspace_id, relationship, "active", _canonical(policy or {}), now, now),
            )
            self._audit("link", "institution_workspace", link_id, workspace_id=workspace_id, actor=actor, details={"institution_id": institution_id})
        row = self.connection.execute("SELECT * FROM institution_workspaces WHERE link_id=?", (link_id,)).fetchone()
        return self._decode_platform(row, "policy")

    def check_platform_permission(self, institution_id: str, principal_id: str, permission: str, *, workspace_id: Optional[str] = None) -> bool:
        row = self.connection.execute(
            "SELECT * FROM institution_members WHERE institution_id=? AND principal_id=? AND status='active'", (institution_id, principal_id)
        ).fetchone()
        if not row:
            return False
        member = self._decode_platform(row, "permissions", "metadata")
        if member["role"] in {"owner", "administrator"}:
            allowed = True
        else:
            allowed = permission in set(member["permissions"])
        if workspace_id:
            allowed = allowed and bool(self.connection.execute(
                "SELECT 1 FROM institution_workspaces WHERE institution_id=? AND workspace_id=? AND status='active'",
                (institution_id, workspace_id),
            ).fetchone())
        return allowed

    def register_platform_connection(self, connection: Dict[str, Any], *, institution_id: str, actor: str = "system") -> Dict[str, Any]:
        self.get_institution(institution_id)
        destination = str(connection.get("destination") or "").strip()
        connection_type = str(connection.get("connection_type") or "internal_module")
        if not destination:
            raise PlatformError("connection destination is required")
        if connection_type not in CONNECTION_TYPES:
            raise PlatformError(f"unsupported connection type: {connection_type}")
        connection_id = str(connection.get("connection_id") or _id("connection", institution_id, destination, connection_type))
        now = _now()
        with self._platform_transaction():
            self.connection.execute(
                """INSERT INTO platform_connections(connection_id,institution_id,destination,connection_type,status,contract_version,
                capabilities_json,config_json,created_at,updated_at,last_verified_at,verification_json,metadata_json)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(institution_id,destination,connection_type) DO UPDATE SET
                status=excluded.status,contract_version=excluded.contract_version,capabilities_json=excluded.capabilities_json,
                config_json=excluded.config_json,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (connection_id, institution_id, destination, connection_type, str(connection.get("status") or "configured"),
                 str(connection.get("contract_version") or "1.0.0"), _canonical(connection.get("capabilities") or []),
                 _canonical(connection.get("config") or {}), now, now, None, _canonical({}), _canonical(connection.get("metadata") or {})),
            )
            self._audit("register", "platform_connection", connection_id, actor=actor, details={"destination": destination})
        return self.get_platform_connection(connection_id)

    def get_platform_connection(self, connection_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM platform_connections WHERE connection_id=?", (connection_id,)).fetchone()
        if not row:
            raise PlatformError(f"platform connection not found: {connection_id}")
        return self._decode_platform(row, "capabilities", "config", "verification", "metadata")

    def verify_platform_connection(self, connection_id: str, verification: Optional[Dict[str, Any]] = None, *, actor: str = "system") -> Dict[str, Any]:
        connection = self.get_platform_connection(connection_id)
        checks = dict(verification or {})
        checks.setdefault("contract_version_present", bool(connection.get("contract_version")))
        checks.setdefault("capabilities_declared", bool(connection.get("capabilities")))
        status = "verified" if all(bool(v) for v in checks.values()) else "needs_attention"
        now = _now()
        with self._platform_transaction():
            self.connection.execute("UPDATE platform_connections SET status=?,last_verified_at=?,verification_json=?,updated_at=? WHERE connection_id=?",
                                    (status, now, _canonical(checks), now, connection_id))
            self._audit("verify", "platform_connection", connection_id, actor=actor, details={"status": status})
        return self.get_platform_connection(connection_id)

    def create_decision_pathway(self, pathway: Dict[str, Any], *, institution_id: str, workspace_id: str, actor: str = "system") -> Dict[str, Any]:
        self.link_institution_workspace(institution_id, workspace_id, relationship=str(pathway.get("relationship") or "managed"), actor=actor)
        nodes = list(pathway.get("nodes") or [])
        edges = list(pathway.get("edges") or [])
        node_ids = {str(node.get("id")) for node in nodes if node.get("id")}
        if len(node_ids) != len(nodes):
            raise PlatformError("decision pathway nodes require unique IDs")
        for edge in edges:
            if str(edge.get("from")) not in node_ids or str(edge.get("to")) not in node_ids:
                raise PlatformError("decision pathway edge references an unknown node")
        title = str(pathway.get("title") or "").strip()
        if not title:
            raise PlatformError("decision pathway title is required")
        pathway_id = str(pathway.get("pathway_id") or _id("pathway", institution_id, workspace_id, title))
        now = _now()
        with self._platform_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO decision_pathways(pathway_id,institution_id,workspace_id,initiative_id,title,status,
                nodes_json,edges_json,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (pathway_id, institution_id, workspace_id, pathway.get("initiative_id"), title,
                 str(pathway.get("status") or "draft"), _canonical(nodes), _canonical(edges), now, now,
                 _canonical(pathway.get("metadata") or {})),
            )
            self._audit("create", "decision_pathway", pathway_id, workspace_id=workspace_id, initiative_id=pathway.get("initiative_id"), actor=actor)
        return self.get_decision_pathway(pathway_id)

    def get_decision_pathway(self, pathway_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM decision_pathways WHERE pathway_id=?", (pathway_id,)).fetchone()
        if not row:
            raise PlatformError(f"decision pathway not found: {pathway_id}")
        return self._decode_platform(row, "nodes", "edges", "metadata")

    def create_platform_workflow(self, workflow: Dict[str, Any], *, institution_id: str, workspace_id: str, actor: str = "system") -> Dict[str, Any]:
        workflow_type = str(workflow.get("workflow_type") or "custom")
        if workflow_type not in WORKFLOW_TYPES:
            raise PlatformError(f"unsupported workflow type: {workflow_type}")
        steps = list(workflow.get("steps") or [])
        for step in steps:
            if str(step.get("type")) not in WORKFLOW_STEP_TYPES:
                raise PlatformError(f"unsupported workflow step: {step.get('type')}")
        name = str(workflow.get("name") or "").strip()
        if not name:
            raise PlatformError("workflow name is required")
        self.link_institution_workspace(institution_id, workspace_id, relationship="managed", actor=actor)
        workflow_id = str(workflow.get("workflow_id") or _id("workflow", institution_id, workspace_id, name))
        now = _now()
        with self._platform_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO platform_workflows(workflow_id,institution_id,workspace_id,name,workflow_type,status,
                trigger_type,steps_json,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (workflow_id, institution_id, workspace_id, name, workflow_type, str(workflow.get("status") or "active"),
                 str(workflow.get("trigger_type") or "manual"), _canonical(steps), now, now, _canonical(workflow.get("metadata") or {})),
            )
            self._audit("create", "platform_workflow", workflow_id, workspace_id=workspace_id, actor=actor)
        return self.get_platform_workflow(workflow_id)

    def get_platform_workflow(self, workflow_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM platform_workflows WHERE workflow_id=?", (workflow_id,)).fetchone()
        if not row:
            raise PlatformError(f"platform workflow not found: {workflow_id}")
        return self._decode_platform(row, "steps", "metadata")

    def run_platform_workflow(self, workflow_id: str, *, inputs: Optional[Dict[str, Any]] = None, actor: str = "system") -> Dict[str, Any]:
        workflow = self.get_platform_workflow(workflow_id)
        if workflow["status"] != "active":
            raise PlatformError("workflow is not active")
        inputs = dict(inputs or {})
        input_hash = _hash(inputs)
        run_id = _id("workflow-run", workflow_id, input_hash, _now())
        started = _now()
        results: List[Dict[str, Any]] = []
        status = "completed"
        try:
            for index, step in enumerate(workflow["steps"]):
                step_type = step["type"]
                if step_type == "repository_integrity":
                    result = self.platform_integrity_report(workflow["institution_id"], workspace_id=workflow["workspace_id"])
                elif step_type == "create_snapshot":
                    result = self.create_platform_snapshot(workflow["institution_id"], workflow["workspace_id"], actor=actor)
                elif step_type == "release_readiness":
                    result = self.evaluate_release_readiness(workflow["workspace_id"], release_version=PLATFORM_VERSION, actor=actor)
                elif step_type == "platform_handoff":
                    result = self.create_platform_handoff(
                        str(step.get("destination") or inputs.get("destination") or "platform_core"),
                        workspace_id=workflow["workspace_id"], initiative_id=step.get("initiative_id") or inputs.get("initiative_id"),
                        actor=actor,
                    )
                else:
                    result = self.emit_platform_event(
                        str(step.get("event_type") or "workflow.event"), subject_type="platform_workflow", subject_id=workflow_id,
                        institution_id=workflow["institution_id"], workspace_id=workflow["workspace_id"], payload=inputs,
                        correlation_id=run_id, actor=actor,
                    )
                results.append({"index": index, "type": step_type, "status": "completed", "result_hash": _hash(result), "result": result})
        except Exception as exc:
            status = "failed"
            results.append({"index": len(results), "status": "failed", "error": str(exc)})
        completed = _now()
        output_hash = _hash(results)
        with self._platform_transaction():
            self.connection.execute(
                """INSERT INTO platform_workflow_runs(run_id,workflow_id,workspace_id,status,input_hash,output_hash,started_at,
                completed_at,step_results_json,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (run_id, workflow_id, workflow["workspace_id"], status, input_hash, output_hash, started, completed,
                 _canonical(results), _canonical({"actor": actor})),
            )
            self._audit("run", "platform_workflow", workflow_id, workspace_id=workflow["workspace_id"], actor=actor,
                        details={"run_id": run_id, "status": status})
        return self.get_platform_workflow_run(run_id)

    def get_platform_workflow_run(self, run_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM platform_workflow_runs WHERE run_id=?", (run_id,)).fetchone()
        if not row:
            raise PlatformError(f"platform workflow run not found: {run_id}")
        return self._decode_platform(row, "step_results", "metadata")

    def emit_platform_event(self, event_type: str, *, subject_type: str, subject_id: str, institution_id: Optional[str] = None,
                            workspace_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None,
                            correlation_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        payload = dict(payload or {})
        occurred = _now()
        payload_hash = _hash(payload)
        event_id = _id("platform-event", event_type, subject_type, subject_id, occurred, payload_hash)
        with self._platform_transaction():
            self.connection.execute(
                """INSERT INTO platform_events(event_id,institution_id,workspace_id,event_type,subject_type,subject_id,occurred_at,
                payload_hash,payload_json,correlation_id,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (event_id, institution_id, workspace_id, event_type, subject_type, subject_id, occurred, payload_hash,
                 _canonical(payload), correlation_id, _canonical({"actor": actor})),
            )
        row = self.connection.execute("SELECT * FROM platform_events WHERE event_id=?", (event_id,)).fetchone()
        return self._decode_platform(row, "payload", "metadata")

    def create_platform_snapshot(self, institution_id: str, workspace_id: str, *, actor: str = "system") -> Dict[str, Any]:
        self.get_institution(institution_id)
        if not self.connection.execute("SELECT 1 FROM institution_workspaces WHERE institution_id=? AND workspace_id=? AND status='active'",
                                       (institution_id, workspace_id)).fetchone():
            self.link_institution_workspace(institution_id, workspace_id, relationship="managed", actor=actor)
        repositories = {
            "evidence": self.export_evidence_repository(workspace_id),
            "registry": self.export_indicator_registry(workspace_id),
            "measurement": self.export_measurement_repository(workspace_id),
            "review": self.export_review_workflow(workspace_id),
            "analysis": self.export_analysis_repository(workspace_id),
            "reporting": self.export_reporting_repository(workspace_id),
            "integration": self.export_integration_repository(workspace_id),
            "production": self.export_production_repository(workspace_id),
        }
        source_hashes = {name: _hash(document) for name, document in repositories.items()}
        summary = {
            "repository": self.repository_summary(),
            "publications": repositories["review"].get("integrity", {}).get("publication_count", 0),
            "evidence_items": repositories["evidence"].get("integrity", {}).get("evidence_item_count", 0),
            "analysis_runs": repositories["analysis"].get("integrity", {}).get("analysis_run_count", 0),
            "readiness_checks": repositories["production"].get("integrity", {}).get("readiness_count", 0),
        }
        status = "ready" if repositories["production"].get("integrity", {}).get("valid", False) else "needs_attention"
        generated = _now()
        snapshot_hash = _hash({"institution_id": institution_id, "workspace_id": workspace_id, "source_hashes": source_hashes, "summary": summary})
        snapshot_id = _id("platform-snapshot", institution_id, workspace_id, snapshot_hash)
        with self._platform_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO platform_snapshots(snapshot_id,institution_id,workspace_id,status,source_hashes_json,
                summary_json,generated_at,snapshot_hash,metadata_json) VALUES(?,?,?,?,?,?,?,?,?)""",
                (snapshot_id, institution_id, workspace_id, status, _canonical(source_hashes), _canonical(summary), generated,
                 snapshot_hash, _canonical({"boundary": PLATFORM_BOUNDARY})),
            )
            self._audit("create", "platform_snapshot", snapshot_id, workspace_id=workspace_id, actor=actor)
        row = self.connection.execute("SELECT * FROM platform_snapshots WHERE snapshot_id=?", (snapshot_id,)).fetchone()
        return self._decode_platform(row, "source_hashes", "summary", "metadata")

    def platform_integrity_report(self, institution_id: str, *, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        self.get_institution(institution_id)
        params: List[Any] = [institution_id]
        link_clause = ""
        run_clause = ""
        if workspace_id:
            link_clause = " AND workspace_id=?"
            run_clause = " AND w.workspace_id=?"
            params.append(workspace_id)
        links = self.connection.execute(f"SELECT * FROM institution_workspaces WHERE institution_id=?{link_clause}", params).fetchall()
        member_count = int(self.connection.execute("SELECT COUNT(*) c FROM institution_members WHERE institution_id=? AND status='active'", (institution_id,)).fetchone()["c"])
        connection_rows = self.connection.execute("SELECT status FROM platform_connections WHERE institution_id=?", (institution_id,)).fetchall()
        failed_runs = int(self.connection.execute(
            f"SELECT COUNT(*) c FROM platform_workflow_runs r JOIN platform_workflows w ON w.workflow_id=r.workflow_id WHERE w.institution_id=?{run_clause} AND r.status='failed'",
            params,
        ).fetchone()["c"])
        orphan_links = sum(1 for row in links if not self.connection.execute(
            "SELECT 1 FROM repository_entities WHERE entity_type='workspace' AND entity_id=?", (row["workspace_id"],)
        ).fetchone())
        verified_connections = sum(1 for row in connection_rows if row["status"] == "verified")
        checks = {
            "institution_active": self.get_institution(institution_id)["status"] == "active",
            "active_member_present": member_count > 0,
            "workspace_links_valid": orphan_links == 0 and len(links) > 0,
            "connections_healthy": not connection_rows or verified_connections == len(connection_rows),
            "workflow_runs_healthy": failed_runs == 0,
        }
        return {
            "institution_id": institution_id, "workspace_id": workspace_id, "platform_version": PLATFORM_VERSION,
            "valid": all(checks.values()), "checks": checks, "active_member_count": member_count,
            "workspace_link_count": len(links), "verified_connection_count": verified_connections,
            "connection_count": len(connection_rows), "failed_workflow_run_count": failed_runs,
            "boundary": PLATFORM_BOUNDARY,
        }

    def institution_overview(self, institution_id: str) -> Dict[str, Any]:
        institution = self.get_institution(institution_id)
        members = [self._decode_platform(row, "permissions", "metadata") for row in self.connection.execute(
            "SELECT * FROM institution_members WHERE institution_id=? ORDER BY role,principal_id", (institution_id,)
        ).fetchall()]
        workspaces = [self._decode_platform(row, "policy") for row in self.connection.execute(
            "SELECT * FROM institution_workspaces WHERE institution_id=? ORDER BY workspace_id", (institution_id,)
        ).fetchall()]
        connections = [self._decode_platform(row, "capabilities", "config", "verification", "metadata") for row in self.connection.execute(
            "SELECT * FROM platform_connections WHERE institution_id=? ORDER BY destination", (institution_id,)
        ).fetchall()]
        return {"institution": institution, "members": members, "workspaces": workspaces, "connections": connections,
                "integrity": self.platform_integrity_report(institution_id)}

    def export_platform_repository(self, workspace_id: str) -> Dict[str, Any]:
        institutions = [dict(row) for row in self.connection.execute(
            """SELECT DISTINCT i.* FROM institutions i JOIN institution_workspaces iw ON iw.institution_id=i.institution_id
            WHERE iw.workspace_id=? ORDER BY i.institution_id""", (workspace_id,)
        ).fetchall()]
        institution_ids = [item["institution_id"] for item in institutions]
        def rows(table: str, fields: tuple[str, ...], where: str = "workspace_id=?", params: tuple[Any, ...] = (workspace_id,)) -> List[Dict[str, Any]]:
            return [self._decode_platform(row, *fields) for row in self.connection.execute(f"SELECT * FROM {table} WHERE {where} ORDER BY 1", params).fetchall()]
        members: List[Dict[str, Any]] = []
        connections: List[Dict[str, Any]] = []
        for institution_id in institution_ids:
            members.extend(rows("institution_members", ("permissions", "metadata"), "institution_id=?", (institution_id,)))
            connections.extend(rows("platform_connections", ("capabilities", "config", "verification", "metadata"), "institution_id=?", (institution_id,)))
        for item in institutions:
            item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
        data = {
            "repository_type": "global_impact_platform_repository", "repository_version": PLATFORM_VERSION,
            "workspace_id": workspace_id, "generated_at": _now(), "institutions": institutions,
            "memberships": members, "workspace_links": rows("institution_workspaces", ("policy",)),
            "connections": connections, "decision_pathways": rows("decision_pathways", ("nodes", "edges", "metadata")),
            "workflows": rows("platform_workflows", ("steps", "metadata")),
            "workflow_runs": rows("platform_workflow_runs", ("step_results", "metadata")),
            "snapshots": rows("platform_snapshots", ("source_hashes", "summary", "metadata")),
            "events": rows("platform_events", ("payload", "metadata")), "boundary": PLATFORM_BOUNDARY,
        }
        data["integrity"] = {
            "valid": all(self.platform_integrity_report(i)["valid"] for i in institution_ids) if institution_ids else True,
            "institution_count": len(institutions), "membership_count": len(members), "workspace_link_count": len(data["workspace_links"]),
            "connection_count": len(connections), "pathway_count": len(data["decision_pathways"]),
            "workflow_count": len(data["workflows"]), "workflow_run_count": len(data["workflow_runs"]),
            "snapshot_count": len(data["snapshots"]), "event_count": len(data["events"]),
        }
        return data

    def _restore_platform_repository(self, repository: Dict[str, Any], *, actor: str = "restore") -> None:
        if not repository:
            return
        with self._platform_transaction():
            table_map = [
                ("institutions", "institutions", ("metadata",)),
                ("memberships", "institution_members", ("permissions", "metadata")),
                ("workspace_links", "institution_workspaces", ("policy",)),
                ("connections", "platform_connections", ("capabilities", "config", "verification", "metadata")),
                ("decision_pathways", "decision_pathways", ("nodes", "edges", "metadata")),
                ("workflows", "platform_workflows", ("steps", "metadata")),
                ("workflow_runs", "platform_workflow_runs", ("step_results", "metadata")),
                ("snapshots", "platform_snapshots", ("source_hashes", "summary", "metadata")),
                ("events", "platform_events", ("payload", "metadata")),
            ]
            for key, table, fields in table_map:
                for original in repository.get(key, []):
                    item = dict(original)
                    for field in fields:
                        if field in item:
                            item[f"{field}_json"] = _canonical(item.pop(field))
                    columns = list(item)
                    self.connection.execute(
                        f"INSERT OR REPLACE INTO {table}({','.join(columns)}) VALUES({','.join('?' for _ in columns)})",
                        [item[column] for column in columns],
                    )
            self._audit("restore", "platform_repository", repository.get("workspace_id", ""), workspace_id=repository.get("workspace_id"), actor=actor)
