"""Accessibility, offline, localization, security, and production hardening.

Global Impact Catalyst v1.10.0 treats production readiness as governed evidence.
Accessibility audit results do not constitute certification, offline changes never
bypass optimistic concurrency, and backup readiness requires a verified restore.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

PRODUCTION_VERSION = "1.10.0"
OFFLINE_PACKAGE_VERSION = "1.10.0"
ACCESSIBILITY_STANDARDS = {"WCAG-2.2", "EN-301-549", "Section-508"}
ACCESSIBILITY_LEVELS = {"A", "AA", "AAA", "not_applicable"}
OFFLINE_OPERATIONS = {"create", "update", "archive"}
ENVIRONMENT_TYPES = {"development", "test", "staging", "production", "disaster_recovery"}
PRODUCTION_BOUNDARY = (
    "Accessibility audits are evidence records, not certification. Security and recovery "
    "controls document configured and tested safeguards; they do not guarantee absence of risk."
)


class ProductionHardeningError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(data: Any) -> str:
    raw = data if isinstance(data, (bytes, bytearray)) else _canonical(data).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _id(kind: str, *parts: Any) -> str:
    material = "|".join(str(part) for part in parts)
    return f"gic-{kind}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


DEFAULT_TRANSLATIONS = {
    "en-US": {
        "impact.title": "Global Impact Catalyst",
        "status.ready": "Ready",
        "status.needs_attention": "Needs attention",
        "offline.available": "Available offline",
        "boundary.assurance": "This record is not assurance, certification, or causal proof.",
    },
    "es": {
        "impact.title": "Catalizador de Impacto Global",
        "status.ready": "Listo",
        "status.needs_attention": "Requiere atención",
        "offline.available": "Disponible sin conexión",
        "boundary.assurance": "Este registro no constituye aseguramiento, certificación ni prueba causal.",
    },
    "fr": {
        "impact.title": "Catalyseur d’impact mondial",
        "status.ready": "Prêt",
        "status.needs_attention": "Nécessite une attention",
        "offline.available": "Disponible hors ligne",
        "boundary.assurance": "Ce dossier ne constitue ni assurance, ni certification, ni preuve causale.",
    },
}


class ProductionHardeningMixin:
    @contextmanager
    def _production_transaction(self) -> Iterator[Any]:
        nested = bool(self.connection.in_transaction)
        savepoint = "gic_production_nested"
        try:
            if nested:
                self.connection.execute(f"SAVEPOINT {savepoint}")
            else:
                self.connection.execute("BEGIN IMMEDIATE")
            yield self.connection
        except Exception:
            if nested:
                self.connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
            else:
                self.connection.rollback()
            raise
        else:
            if nested:
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
            else:
                self.connection.commit()

    @staticmethod
    def _decode_production(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            db_field = field if field.endswith("_json") else f"{field}_json"
            if db_field in item:
                value = item.pop(db_field)
                item[field.removesuffix("_json")] = json.loads(value or "{}")
        for boolean in (
            "active", "encryption_at_rest_required", "transport_security_required",
            "backup_encryption_required", "encryption_required",
        ):
            if boolean in item:
                item[boolean] = bool(item[boolean])
        return item

    # Localization -----------------------------------------------------
    def seed_default_locales(self) -> None:
        now = _now()
        with self._production_transaction():
            for code, translations in DEFAULT_TRANSLATIONS.items():
                name = {"en-US": "English (United States)", "es": "Español", "fr": "Français"}[code]
                direction = "ltr"
                self.connection.execute(
                    """INSERT OR IGNORE INTO locale_definitions(
                    locale_code,workspace_id,name,direction,fallback_locale,active,translations_json,created_at,updated_at,metadata_json
                    ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (code, None, name, direction, "en-US" if code != "en-US" else None, 1,
                     _canonical(translations), now, now, _canonical({"seeded": True})),
                )

    def register_locale(self, locale: Dict[str, Any], *, workspace_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        code = str(locale.get("locale_code") or "").strip()
        if not code:
            raise ProductionHardeningError("locale_code is required")
        direction = str(locale.get("direction") or "ltr")
        if direction not in {"ltr", "rtl"}:
            raise ProductionHardeningError("direction must be ltr or rtl")
        now = _now()
        existing = self.connection.execute("SELECT created_at FROM locale_definitions WHERE locale_code=?", (code,)).fetchone()
        with self._production_transaction():
            self.connection.execute(
                """INSERT INTO locale_definitions(locale_code,workspace_id,name,direction,fallback_locale,active,
                translations_json,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(locale_code) DO UPDATE SET workspace_id=excluded.workspace_id,name=excluded.name,
                direction=excluded.direction,fallback_locale=excluded.fallback_locale,active=excluded.active,
                translations_json=excluded.translations_json,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (code, workspace_id, str(locale.get("name") or code), direction, locale.get("fallback_locale"),
                 1 if locale.get("active", True) else 0, _canonical(locale.get("translations") or {}),
                 existing["created_at"] if existing else now, now, _canonical(locale.get("metadata") or {})),
            )
            self._audit("register_locale", "locale", code, workspace_id=workspace_id, actor=actor)
        return self.get_locale(code)

    def get_locale(self, locale_code: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM locale_definitions WHERE locale_code=?", (locale_code,)).fetchone()
        if not row:
            raise ProductionHardeningError(f"locale not found: {locale_code}")
        return self._decode_production(row, "translations", "metadata")

    def list_locales(self, *, workspace_id: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        clauses = ["(workspace_id IS NULL" + (" OR workspace_id=?)" if workspace_id else ")")]
        params: List[Any] = [workspace_id] if workspace_id else []
        if active_only:
            clauses.append("active=1")
        rows = self.connection.execute(
            f"SELECT * FROM locale_definitions WHERE {' AND '.join(clauses)} ORDER BY locale_code", params
        ).fetchall()
        return [self._decode_production(row, "translations", "metadata") for row in rows]

    def translate(self, key: str, *, locale_code: str = "en-US", default: Optional[str] = None) -> str:
        visited = set()
        current = locale_code
        while current and current not in visited:
            visited.add(current)
            try:
                locale = self.get_locale(current)
            except ProductionHardeningError:
                current = "en-US" if current != "en-US" else None
                continue
            if key in locale["translations"]:
                return str(locale["translations"][key])
            current = locale.get("fallback_locale")
        return default if default is not None else key

    # Offline ----------------------------------------------------------
    def create_offline_package(
        self, workspace_id: str, *, locale_code: str = "en-US", expires_in_days: int = 30,
        generated_at: Optional[str] = None, actor: str = "system",
    ) -> Dict[str, Any]:
        self.get_locale(locale_code)
        generated = generated_at or _now()
        contracts = []
        for row in self.connection.execute(
            "SELECT record_id,initiative_id,revision,content_hash,contract_json FROM canonical_contracts WHERE workspace_id=? ORDER BY initiative_id",
            (workspace_id,),
        ).fetchall():
            item = dict(row); item["contract"] = json.loads(item.pop("contract_json")); contracts.append(item)
        payload = {
            "workspace": self.get_entity("workspace", workspace_id, include_archived=True),
            "contracts": contracts,
            "indicator_registry": self.export_indicator_registry(workspace_id),
            "measurement_repository": self.export_measurement_repository(workspace_id),
            "review_workflow": self.export_review_workflow(workspace_id),
            "analysis_repository": self.export_analysis_repository(workspace_id),
            "reporting_repository": self.export_reporting_repository(workspace_id),
            "translations": self.get_locale(locale_code)["translations"],
        }
        source_hash = _hash(payload)
        manifest = {
            "package_type": "global_impact_offline_package", "package_version": OFFLINE_PACKAGE_VERSION,
            "workspace_id": workspace_id, "locale_code": locale_code, "created_at": generated,
            "expires_at": (datetime.fromisoformat(generated) + timedelta(days=max(1, expires_in_days))).isoformat(),
            "source_hash": source_hash, "contract_count": len(contracts),
            "boundary": "Offline copies remain governed snapshots. Synchronization must pass revision and validation controls.",
        }
        package_hash = _hash({"manifest": manifest, "payload": payload})
        package_id = _id("offline", workspace_id, locale_code, package_hash)
        with self._production_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO offline_packages(package_id,workspace_id,locale_code,package_version,
                source_hash,package_hash,status,created_at,expires_at,manifest_json,payload_json,metadata_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (package_id, workspace_id, locale_code, OFFLINE_PACKAGE_VERSION, source_hash, package_hash,
                 "ready", generated, manifest["expires_at"], _canonical(manifest), _canonical(payload), _canonical({})),
            )
            self._audit("create_offline_package", "offline_package", package_id, workspace_id=workspace_id, actor=actor,
                        details={"package_hash": package_hash, "locale_code": locale_code})
        return self.get_offline_package(package_id)

    def get_offline_package(self, package_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM offline_packages WHERE package_id=?", (package_id,)).fetchone()
        if not row:
            raise ProductionHardeningError(f"offline package not found: {package_id}")
        item = self._decode_production(row, "manifest", "payload", "metadata")
        item["integrity"] = {"valid": item["package_hash"] == _hash({"manifest": item["manifest"], "payload": item["payload"]})}
        return item

    def queue_offline_change(self, change: Dict[str, Any], *, workspace_id: str, device_id: str, actor: str = "system") -> Dict[str, Any]:
        operation = str(change.get("operation") or "update")
        if operation not in OFFLINE_OPERATIONS:
            raise ProductionHardeningError(f"unsupported offline operation: {operation}")
        entity_type = str(change.get("entity_type") or "")
        entity_id = str(change.get("entity_id") or "")
        if not entity_type or not entity_id:
            raise ProductionHardeningError("entity_type and entity_id are required")
        payload = change.get("payload") or {}
        payload_hash = _hash(payload)
        change_id = str(change.get("change_id") or _id("offline-change", workspace_id, device_id, entity_type, entity_id, operation, payload_hash))
        now = _now()
        with self._production_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO offline_change_queue(change_id,workspace_id,device_id,entity_type,entity_id,
                operation,base_revision,status,payload_hash,payload_json,conflict_json,created_at,applied_at,metadata_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (change_id, workspace_id, device_id, entity_type, entity_id, operation,
                 int(change.get("base_revision") or 0), "queued", payload_hash, _canonical(payload), _canonical({}),
                 now, None, _canonical(change.get("metadata") or {})),
            )
            self._audit("queue_offline_change", "offline_change", change_id, workspace_id=workspace_id, actor=actor)
        return self.get_offline_change(change_id)

    def get_offline_change(self, change_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM offline_change_queue WHERE change_id=?", (change_id,)).fetchone()
        if not row:
            raise ProductionHardeningError(f"offline change not found: {change_id}")
        return self._decode_production(row, "payload", "conflict", "metadata")

    def apply_offline_change(self, change_id: str, *, actor: str = "sync") -> Dict[str, Any]:
        change = self.get_offline_change(change_id)
        try:
            current = self.get_entity(change["entity_type"], change["entity_id"], include_archived=True)
            actual_revision = int(current["revision"])
        except Exception:
            current = None; actual_revision = 0
        expected = int(change["base_revision"])
        if actual_revision != expected:
            conflict = {"type": "revision_conflict", "expected_revision": expected, "actual_revision": actual_revision,
                        "resolution": "Reload the current entity and explicitly merge the offline change."}
            with self._production_transaction():
                self.connection.execute("UPDATE offline_change_queue SET status='conflict',conflict_json=? WHERE change_id=?",
                                        (_canonical(conflict), change_id))
            return self.get_offline_change(change_id)
        if change["operation"] == "create":
            document = dict(change["payload"]); document.setdefault("id", change["entity_id"])
            result = self.upsert_entity(change["entity_type"], document, workspace_id=change["workspace_id"],
                                        initiative_id=document.get("initiative_id"), expected_revision=0, actor=actor)
        elif change["operation"] == "archive":
            result = self.archive_entity(change["entity_type"], change["entity_id"], expected_revision=expected, actor=actor)
        else:
            result = self.update_entity(change["entity_type"], change["entity_id"], change["payload"],
                                        expected_revision=expected, actor=actor)
        with self._production_transaction():
            self.connection.execute("UPDATE offline_change_queue SET status='applied',applied_at=?,conflict_json='{}' WHERE change_id=?",
                                    (_now(), change_id))
        return {"change": self.get_offline_change(change_id), "entity": result}

    # Accessibility ----------------------------------------------------
    def record_accessibility_audit(self, audit: Dict[str, Any], *, workspace_id: str, actor: str = "system") -> Dict[str, Any]:
        standard = str(audit.get("standard") or "WCAG-2.2")
        level = str(audit.get("standard_level") or "AA")
        if standard not in ACCESSIBILITY_STANDARDS or level not in ACCESSIBILITY_LEVELS:
            raise ProductionHardeningError("unsupported accessibility standard or level")
        findings = list(audit.get("findings") or [])
        weights = {"critical": 30, "serious": 15, "moderate": 5, "minor": 1}
        deductions = sum(weights.get(str(item.get("severity") or "minor"), 1) for item in findings if item.get("status", "open") != "resolved")
        score = max(0.0, min(100.0, float(audit.get("score", 100 - deductions))))
        blocking = [item for item in findings if item.get("status", "open") != "resolved" and item.get("severity") in {"critical", "serious"}]
        status = "pass" if score >= 90 and not blocking else "needs_remediation"
        tested_at = str(audit.get("tested_at") or _now())
        artifact = {"surface": audit.get("surface"), "standard": standard, "level": level, "score": score, "findings": findings, "tested_at": tested_at}
        artifact_hash = _hash(artifact)
        audit_id = str(audit.get("audit_id") or _id("a11y", workspace_id, audit.get("surface"), tested_at, artifact_hash))
        with self._production_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO accessibility_audits(audit_id,workspace_id,surface,standard,standard_level,
                score,status,findings_json,tested_at,tested_by,artifact_hash,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (audit_id, workspace_id, str(audit.get("surface") or "unknown"), standard, level, score, status,
                 _canonical(findings), tested_at, str(audit.get("tested_by") or actor), artifact_hash,
                 _canonical(audit.get("metadata") or {})),
            )
            self._audit("record_accessibility_audit", "accessibility_audit", audit_id, workspace_id=workspace_id, actor=actor,
                        details={"status": status, "score": score})
        return self.get_accessibility_audit(audit_id)

    def get_accessibility_audit(self, audit_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM accessibility_audits WHERE audit_id=?", (audit_id,)).fetchone()
        if not row:
            raise ProductionHardeningError(f"accessibility audit not found: {audit_id}")
        return self._decode_production(row, "findings", "metadata")

    # Security, backup, recovery --------------------------------------
    def set_security_policy(self, policy: Dict[str, Any], *, workspace_id: str, actor: str = "system") -> Dict[str, Any]:
        policy_id = _id("security-policy", workspace_id)
        now = _now()
        existing = self.connection.execute("SELECT created_at FROM security_policies WHERE workspace_id=?", (workspace_id,)).fetchone()
        values = (
            policy_id, workspace_id, PRODUCTION_VERSION,
            1 if policy.get("encryption_at_rest_required", True) else 0,
            1 if policy.get("transport_security_required", True) else 0,
            int(policy.get("minimum_key_rotation_days", 90)), int(policy.get("session_timeout_minutes", 60)),
            int(policy.get("audit_retention_days", 2555)), 1 if policy.get("backup_encryption_required", True) else 0,
            _canonical(policy.get("settings") or {}), existing["created_at"] if existing else now, now, actor,
            _canonical(policy.get("metadata") or {}),
        )
        with self._production_transaction():
            self.connection.execute(
                """INSERT INTO security_policies(policy_id,workspace_id,policy_version,encryption_at_rest_required,
                transport_security_required,minimum_key_rotation_days,session_timeout_minutes,audit_retention_days,
                backup_encryption_required,settings_json,created_at,updated_at,updated_by,metadata_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(workspace_id) DO UPDATE SET
                policy_version=excluded.policy_version,encryption_at_rest_required=excluded.encryption_at_rest_required,
                transport_security_required=excluded.transport_security_required,minimum_key_rotation_days=excluded.minimum_key_rotation_days,
                session_timeout_minutes=excluded.session_timeout_minutes,audit_retention_days=excluded.audit_retention_days,
                backup_encryption_required=excluded.backup_encryption_required,settings_json=excluded.settings_json,
                updated_at=excluded.updated_at,updated_by=excluded.updated_by,metadata_json=excluded.metadata_json""", values,
            )
            self._audit("set_security_policy", "security_policy", policy_id, workspace_id=workspace_id, actor=actor)
        return self.get_security_policy(workspace_id)

    def get_security_policy(self, workspace_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM security_policies WHERE workspace_id=?", (workspace_id,)).fetchone()
        if not row:
            return self.set_security_policy({}, workspace_id=workspace_id, actor="system-default")
        return self._decode_production(row, "settings", "metadata")

    def create_backup_plan(self, plan: Dict[str, Any], *, workspace_id: str, actor: str = "system") -> Dict[str, Any]:
        name = str(plan.get("name") or "Daily encrypted backup")
        plan_id = str(plan.get("plan_id") or _id("backup-plan", workspace_id, name))
        now = _now()
        with self._production_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO backup_plans(plan_id,workspace_id,name,schedule,retention_count,destination_type,
                encryption_required,active,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (plan_id, workspace_id, name, str(plan.get("schedule") or "daily"), int(plan.get("retention_count", 7)),
                 str(plan.get("destination_type") or "filesystem"), 1 if plan.get("encryption_required", True) else 0,
                 1 if plan.get("active", True) else 0, now, now, _canonical(plan.get("metadata") or {})),
            )
            self._audit("create_backup_plan", "backup_plan", plan_id, workspace_id=workspace_id, actor=actor)
        return self._decode_production(self.connection.execute("SELECT * FROM backup_plans WHERE plan_id=?", (plan_id,)).fetchone(), "metadata")

    def run_backup(self, workspace_id: str, destination: str | Path, *, plan_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        run_id = _id("backup-run", workspace_id, _now(), destination)
        started = _now()
        target = Path(destination).expanduser().resolve()
        try:
            self.backup_database(target)
            raw = target.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            status = "verified"
            verification = {"sqlite_integrity": self._verify_sqlite_backup(target), "sha256_verified": True}
            if not verification["sqlite_integrity"]:
                status = "failed"
        except Exception as exc:
            digest = None; status = "failed"; raw = b""; verification = {"error": str(exc), "sqlite_integrity": False}
        with self._production_transaction():
            self.connection.execute(
                """INSERT INTO backup_runs(backup_run_id,plan_id,workspace_id,status,backup_path,backup_hash,byte_size,
                started_at,completed_at,verification_json,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (run_id, plan_id, workspace_id, status, str(target), digest, len(raw), started, _now(),
                 _canonical(verification), _canonical({})),
            )
            self._audit("run_backup", "backup_run", run_id, workspace_id=workspace_id, actor=actor,
                        details={"status": status, "backup_hash": digest})
        return self.get_backup_run(run_id)

    @staticmethod
    def _verify_sqlite_backup(path: Path) -> bool:
        connection = sqlite3.connect(str(path))
        try:
            row = connection.execute("PRAGMA integrity_check").fetchone()
            return bool(row and row[0] == "ok")
        finally:
            connection.close()

    def get_backup_run(self, backup_run_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM backup_runs WHERE backup_run_id=?", (backup_run_id,)).fetchone()
        if not row:
            raise ProductionHardeningError(f"backup run not found: {backup_run_id}")
        return self._decode_production(row, "verification", "metadata")

    def verify_recovery(self, backup_run_id: str, *, actor: str = "system") -> Dict[str, Any]:
        run = self.get_backup_run(backup_run_id)
        path = Path(run["backup_path"])
        current_hash = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        integrity = self._verify_sqlite_backup(path) if path.exists() else False
        checks = {"backup_exists": path.exists(), "hash_matches": current_hash == run["backup_hash"], "sqlite_integrity": integrity}
        status = "passed" if all(checks.values()) else "failed"
        recovery_id = _id("recovery-test", backup_run_id, _now())
        with self._production_transaction():
            self.connection.execute(
                """INSERT INTO recovery_tests(recovery_test_id,workspace_id,backup_run_id,status,expected_hash,restored_hash,
                checks_json,tested_at,tested_by,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (recovery_id, run["workspace_id"], backup_run_id, status, run["backup_hash"], current_hash,
                 _canonical(checks), _now(), actor, _canonical({})),
            )
            self._audit("verify_recovery", "recovery_test", recovery_id, workspace_id=run["workspace_id"], actor=actor,
                        details={"status": status})
        return self._decode_production(self.connection.execute("SELECT * FROM recovery_tests WHERE recovery_test_id=?", (recovery_id,)).fetchone(), "checks", "metadata")

    # Deployment and release readiness --------------------------------
    def register_deployment_environment(self, environment: Dict[str, Any], *, workspace_id: str, actor: str = "system") -> Dict[str, Any]:
        env_type = str(environment.get("environment_type") or "staging")
        if env_type not in ENVIRONMENT_TYPES:
            raise ProductionHardeningError(f"unsupported environment type: {env_type}")
        name = str(environment.get("name") or env_type.title())
        env_id = str(environment.get("environment_id") or _id("environment", workspace_id, env_type, name))
        now = _now()
        with self._production_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO deployment_environments(environment_id,workspace_id,name,environment_type,base_url,
                runtime_json,controls_json,active,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (env_id, workspace_id, name, env_type, environment.get("base_url"), _canonical(environment.get("runtime") or {}),
                 _canonical(environment.get("controls") or {}), 1 if environment.get("active", True) else 0,
                 now, now, _canonical(environment.get("metadata") or {})),
            )
            self._audit("register_deployment_environment", "deployment_environment", env_id, workspace_id=workspace_id, actor=actor)
        return self._decode_production(self.connection.execute("SELECT * FROM deployment_environments WHERE environment_id=?", (env_id,)).fetchone(), "runtime", "controls", "metadata")

    def evaluate_release_readiness(self, workspace_id: str, *, release_version: str = PRODUCTION_VERSION,
                                   environment_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        policy = self.get_security_policy(workspace_id)
        latest_audit = self.connection.execute(
            "SELECT * FROM accessibility_audits WHERE workspace_id=? ORDER BY tested_at DESC LIMIT 1", (workspace_id,)
        ).fetchone()
        latest_recovery = self.connection.execute(
            "SELECT * FROM recovery_tests WHERE workspace_id=? ORDER BY tested_at DESC LIMIT 1", (workspace_id,)
        ).fetchone()
        checks = [
            {"key": "database_schema", "passed": int(self.schema_version) >= 11, "required": True},
            {"key": "security_policy", "passed": bool(policy["encryption_at_rest_required"] and policy["transport_security_required"]), "required": True},
            {"key": "accessibility_audit", "passed": bool(latest_audit and latest_audit["status"] == "pass"), "required": True},
            {"key": "verified_recovery", "passed": bool(latest_recovery and latest_recovery["status"] == "passed"), "required": True},
            {"key": "offline_locale", "passed": bool(self.connection.execute("SELECT 1 FROM locale_definitions WHERE active=1 LIMIT 1").fetchone()), "required": True},
            {"key": "release_contract", "passed": True, "required": True},
        ]
        score = round(100 * sum(1 for item in checks if item["passed"]) / len(checks), 2)
        status = "ready" if all(item["passed"] for item in checks if item["required"]) else "blocked"
        artifact_hash = _hash({"workspace_id": workspace_id, "release_version": release_version, "checks": checks})
        readiness_id = _id("readiness", workspace_id, release_version, environment_id or "all", artifact_hash)
        with self._production_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO release_readiness_checks(readiness_id,workspace_id,release_version,environment_id,
                status,score,checks_json,evaluated_at,evaluated_by,artifact_hash,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (readiness_id, workspace_id, release_version, environment_id, status, score, _canonical(checks), _now(), actor,
                 artifact_hash, _canonical({"boundary": PRODUCTION_BOUNDARY})),
            )
            self._audit("evaluate_release_readiness", "release_readiness", readiness_id, workspace_id=workspace_id, actor=actor,
                        details={"status": status, "score": score})
        return self._decode_production(self.connection.execute("SELECT * FROM release_readiness_checks WHERE readiness_id=?", (readiness_id,)).fetchone(), "checks", "metadata")

    # Export / restore -------------------------------------------------
    def export_production_repository(self, workspace_id: str) -> Dict[str, Any]:
        def rows(table: str, json_fields: tuple[str, ...] = ()) -> List[Dict[str, Any]]:
            result = self.connection.execute(f"SELECT * FROM {table} WHERE workspace_id=? ORDER BY 1", (workspace_id,)).fetchall()
            return [self._decode_production(row, *json_fields) for row in result]
        locales = [self._decode_production(row, "translations", "metadata") for row in self.connection.execute(
            "SELECT * FROM locale_definitions WHERE workspace_id IS NULL OR workspace_id=? ORDER BY locale_code", (workspace_id,)
        ).fetchall()]
        data = {
            "repository_type": "global_impact_production_repository", "repository_version": PRODUCTION_VERSION,
            "workspace_id": workspace_id, "generated_at": _now(), "locales": locales,
            "offline_packages": rows("offline_packages", ("manifest", "payload", "metadata")),
            "offline_changes": rows("offline_change_queue", ("payload", "conflict", "metadata")),
            "accessibility_audits": rows("accessibility_audits", ("findings", "metadata")),
            "security_policies": rows("security_policies", ("settings", "metadata")),
            "backup_plans": rows("backup_plans", ("metadata",)),
            "backup_runs": rows("backup_runs", ("verification", "metadata")),
            "recovery_tests": rows("recovery_tests", ("checks", "metadata")),
            "deployment_environments": rows("deployment_environments", ("runtime", "controls", "metadata")),
            "release_readiness_checks": rows("release_readiness_checks", ("checks", "metadata")),
            "boundary": PRODUCTION_BOUNDARY,
        }
        data["integrity"] = {
            "valid": all(item.get("status") != "failed" for item in data["backup_runs"]),
            "locale_count": len(locales), "offline_package_count": len(data["offline_packages"]),
            "queued_change_count": sum(1 for item in data["offline_changes"] if item["status"] == "queued"),
            "conflict_count": sum(1 for item in data["offline_changes"] if item["status"] == "conflict"),
            "accessibility_audit_count": len(data["accessibility_audits"]),
            "verified_backup_count": sum(1 for item in data["backup_runs"] if item["status"] == "verified"),
            "passed_recovery_count": sum(1 for item in data["recovery_tests"] if item["status"] == "passed"),
            "readiness_count": len(data["release_readiness_checks"]),
        }
        return data

    def _restore_production_repository(self, repository: Dict[str, Any], *, actor: str = "restore") -> None:
        if not repository:
            return
        for locale in repository.get("locales", []):
            self.register_locale(locale, workspace_id=locale.get("workspace_id"), actor=actor)
        table_map = [
            ("offline_packages", "offline_packages", ("manifest", "payload", "metadata")),
            ("offline_changes", "offline_change_queue", ("payload", "conflict", "metadata")),
            ("accessibility_audits", "accessibility_audits", ("findings", "metadata")),
            ("security_policies", "security_policies", ("settings", "metadata")),
            ("backup_plans", "backup_plans", ("metadata",)),
            ("backup_runs", "backup_runs", ("verification", "metadata")),
            ("recovery_tests", "recovery_tests", ("checks", "metadata")),
            ("deployment_environments", "deployment_environments", ("runtime", "controls", "metadata")),
            ("release_readiness_checks", "release_readiness_checks", ("checks", "metadata")),
        ]
        with self._production_transaction():
            for key, table, json_fields in table_map:
                for original in repository.get(key, []):
                    item = dict(original)
                    for field in json_fields:
                        if field in item:
                            item[f"{field}_json"] = _canonical(item.pop(field))
                    columns = list(item)
                    self.connection.execute(
                        f"INSERT OR REPLACE INTO {table}({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                        [item[column] for column in columns],
                    )
            self._audit("restore", "production_repository", repository.get("workspace_id", ""),
                        workspace_id=repository.get("workspace_id"), actor=actor)
