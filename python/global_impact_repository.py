"""Persistent repository for Global Impact Catalyst v2.0.0.

The repository stores canonical contracts as immutable calculation snapshots and
maintains indexed entity projections for workspace operations. SQLite is the
reference implementation; callers use the same API from CLI, application, and
integration layers.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

from python.global_impact_registry import IndicatorRegistryMixin
from python.global_impact_measurement import MeasurementPortfolioMixin
from python.global_impact_review import ReviewWorkflowMixin
from python.global_impact_analysis import AnalysisScenarioMixin
from python.global_impact_reporting import ReportingPublicationMixin
from python.global_impact_integration import PublicAPIIntegrationMixin
from python.global_impact_production import ProductionHardeningMixin
from python.global_impact_platform import ConnectedImpactPlatformMixin

DATABASE_SCHEMA_VERSION = 12
SUPPORTED_CONTRACT_VERSIONS = {"1.0.0", "1.0.1", "1.1.0", "1.2.0"}
ENTITY_TYPES = {"workspace", "initiative", "goal", "indicator", "observation", "target", "source"}
EVIDENCE_TYPES = {"excerpt", "quotation", "dataset_excerpt", "observation_note", "document_note", "table", "figure"}
CLAIM_EVIDENCE_RELATIONSHIPS = {"supports", "contradicts", "qualifies", "context"}
EVIDENCE_STRENGTHS = {"direct", "indirect", "contextual"}
CHECKSUM_ALGORITHMS = {"sha256"}
SAVE_STATES = {"draft", "saved"}


class RepositoryError(RuntimeError):
    """Base persistence error."""


class NotFoundError(RepositoryError):
    """Raised when a requested repository object does not exist."""


class OptimisticConcurrencyError(RepositoryError):
    """Raised when an update uses a stale revision."""

    def __init__(self, entity_type: str, entity_id: str, expected: int, actual: int):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.expected_revision = expected
        self.actual_revision = actual
        super().__init__(
            f"stale {entity_type} revision for {entity_id}: expected {expected}, current {actual}"
        )


class UnsupportedImportError(RepositoryError):
    """Raised for documents that cannot be migrated into a canonical contract."""


@dataclass(frozen=True)
class ImportResult:
    import_id: str
    record_id: str
    initiative_id: str
    status: str
    content_hash: str
    contract_revision: int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def repository_id(kind: str, *parts: Any) -> str:
    material = "|".join(str(part) for part in parts)
    return f"gic-{kind}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


def checksum_payload(payload: bytes | str, algorithm: str = "sha256") -> str:
    if algorithm not in CHECKSUM_ALGORITHMS:
        raise RepositoryError(f"unsupported checksum algorithm: {algorithm}")
    raw = payload.encode("utf-8") if isinstance(payload, str) else payload
    return hashlib.sha256(raw).hexdigest()


MIGRATIONS: Sequence[tuple[int, str, str]] = (
    (
        1,
        "core_repository",
        """
        CREATE TABLE IF NOT EXISTS repository_entities (
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            workspace_id TEXT,
            initiative_id TEXT,
            parent_id TEXT,
            name TEXT NOT NULL DEFAULT '',
            lifecycle_status TEXT NOT NULL DEFAULT 'draft',
            archived_at TEXT,
            revision INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            document_json TEXT NOT NULL,
            PRIMARY KEY (entity_type, entity_id)
        );
        CREATE INDEX IF NOT EXISTS idx_entities_workspace ON repository_entities(workspace_id, entity_type);
        CREATE INDEX IF NOT EXISTS idx_entities_initiative ON repository_entities(initiative_id, entity_type);
        CREATE INDEX IF NOT EXISTS idx_entities_name ON repository_entities(entity_type, name);

        CREATE TABLE IF NOT EXISTS canonical_contracts (
            record_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            initiative_id TEXT NOT NULL UNIQUE,
            contract_version TEXT NOT NULL,
            save_state TEXT NOT NULL DEFAULT 'saved',
            lifecycle_status TEXT NOT NULL DEFAULT 'draft',
            revision INTEGER NOT NULL DEFAULT 1,
            content_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            contract_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_contracts_workspace ON canonical_contracts(workspace_id, updated_at);
        """,
    ),
    (
        2,
        "portfolios_and_autosave",
        """
        CREATE TABLE IF NOT EXISTS portfolios (
            portfolio_id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            archived_at TEXT,
            revision INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_portfolios_workspace ON portfolios(workspace_id, name);

        CREATE TABLE IF NOT EXISTS portfolio_memberships (
            portfolio_id TEXT NOT NULL,
            initiative_id TEXT NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            added_at TEXT NOT NULL,
            PRIMARY KEY (portfolio_id, initiative_id),
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS draft_autosaves (
            initiative_id TEXT PRIMARY KEY,
            base_revision INTEGER NOT NULL,
            content_hash TEXT NOT NULL,
            saved_at TEXT NOT NULL,
            contract_json TEXT NOT NULL
        );
        """,
    ),
    (
        3,
        "imports_audit_and_bundles",
        """
        CREATE TABLE IF NOT EXISTS import_records (
            import_id TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL UNIQUE,
            source_contract_version TEXT NOT NULL,
            record_id TEXT NOT NULL,
            initiative_id TEXT NOT NULL,
            status TEXT NOT NULL,
            imported_at TEXT NOT NULL,
            metadata_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            occurred_at TEXT NOT NULL,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            workspace_id TEXT,
            initiative_id TEXT,
            revision INTEGER,
            details_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_audit_workspace ON audit_log(workspace_id, occurred_at);
        CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id, occurred_at);

        CREATE TABLE IF NOT EXISTS restore_records (
            restore_id TEXT PRIMARY KEY,
            bundle_hash TEXT NOT NULL UNIQUE,
            restored_at TEXT NOT NULL,
            workspace_id TEXT NOT NULL,
            summary_json TEXT NOT NULL
        );
        """,
    ),
    (
        4,
        "sources_provenance_evidence",
        (Path(__file__).resolve().parents[1] / "migrations/004_sources_provenance_evidence.sql").read_text(encoding="utf-8"),
    ),
    (
        5,
        "indicator_registry_units_baselines_targets_methods",
        (Path(__file__).resolve().parents[1] / "migrations/005_indicator_registry_units_baselines_targets_methods.sql").read_text(encoding="utf-8"),
    ),
    (
        6,
        "observations_beneficiaries_budgets_outcome_portfolios",
        (Path(__file__).resolve().parents[1] / "migrations/006_observations_beneficiaries_budgets_outcome_portfolios.sql").read_text(encoding="utf-8"),
    ),
    (
        7,
        "review_quality_revision_workflow",
        (Path(__file__).resolve().parents[1] / "migrations/007_review_quality_revision_workflow.sql").read_text(encoding="utf-8"),
    ),
    (
        8,
        "trends_comparisons_scenarios_uncertainty",
        (Path(__file__).resolve().parents[1] / "migrations/008_trends_comparisons_scenarios_uncertainty.sql").read_text(encoding="utf-8"),
    ),
    (
        9,
        "reporting_publication_reproducible_exports",
        (Path(__file__).resolve().parents[1] / "migrations/009_reporting_publication_reproducible_exports.sql").read_text(encoding="utf-8"),
    ),
    (
        10,
        "public_api_embeds_platform_handoffs",
        (Path(__file__).resolve().parents[1] / "migrations/010_public_api_embeds_platform_handoffs.sql").read_text(encoding="utf-8"),
    ),
    (
        11,
        "accessibility_offline_localization_production_hardening",
        (Path(__file__).resolve().parents[1] / "migrations/011_accessibility_offline_localization_production_hardening.sql").read_text(encoding="utf-8"),
    ),
    (
        12,
        "connected_public_interest_impact_intelligence_platform",
        (Path(__file__).resolve().parents[1] / "migrations/012_connected_public_interest_impact_intelligence_platform.sql").read_text(encoding="utf-8"),
    ),
)

class SQLiteImpactRepository(ConnectedImpactPlatformMixin, ProductionHardeningMixin, PublicAPIIntegrationMixin, ReportingPublicationMixin, AnalysisScenarioMixin, ReviewWorkflowMixin, MeasurementPortfolioMixin, IndicatorRegistryMixin):
    """SQLite reference repository with repeatable migrations and JSON projections."""

    def __init__(self, database: str | Path = ":memory:", *, auto_migrate: bool = True):
        self.database = str(database)
        if self.database != ":memory:":
            Path(self.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self._ensure_migration_table()
        if auto_migrate:
            self.migrate()

    def _registry_concurrency(self, entity_type: str, entity_id: str, expected: int, actual: int) -> None:
        raise OptimisticConcurrencyError(entity_type, entity_id, expected, actual)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "SQLiteImpactRepository":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            yield self.connection
        except Exception:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def _ensure_migration_table(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    @property
    def schema_version(self) -> int:
        row = self.connection.execute("SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations").fetchone()
        return int(row["version"])

    def migrate(self, target_version: Optional[int] = None) -> int:
        target = DATABASE_SCHEMA_VERSION if target_version is None else int(target_version)
        if target < self.schema_version or target > DATABASE_SCHEMA_VERSION:
            raise RepositoryError(f"unsupported migration target {target}")
        for version, name, sql in MIGRATIONS:
            if self.schema_version < version <= target:
                with self.transaction() as connection:
                    connection.executescript(sql)
                    connection.execute(
                        "INSERT INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
                        (version, name, utc_now()),
                    )
        if self.schema_version >= 5:
            self._seed_standard_units()
        if self.schema_version >= 11:
            self.seed_default_locales()
        return self.schema_version

    def applied_migrations(self) -> List[Dict[str, Any]]:
        return [dict(row) for row in self.connection.execute("SELECT * FROM schema_migrations ORDER BY version")]

    def _audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        *,
        workspace_id: Optional[str] = None,
        initiative_id: Optional[str] = None,
        revision: Optional[int] = None,
        actor: str = "system",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.connection.execute(
            """INSERT INTO audit_log(
                occurred_at, actor, action, entity_type, entity_id, workspace_id,
                initiative_id, revision, details_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                utc_now(), actor, action, entity_type, entity_id, workspace_id,
                initiative_id, revision, canonical_json(details or {}),
            ),
        )

    @staticmethod
    def _entity_name(entity_type: str, document: Dict[str, Any]) -> str:
        if entity_type in {"workspace", "initiative", "indicator", "source"}:
            return str(document.get("name") or document.get("title") or "")
        if entity_type == "goal":
            return str(document.get("statement") or "")
        if entity_type in {"observation", "target"}:
            period = document.get("period") or {}
            return f"{period.get('label', '')} {document.get('value', '')}".strip()
        return str(document.get("name") or document.get("statement") or "")

    def upsert_entity(
        self,
        entity_type: str,
        document: Dict[str, Any],
        *,
        workspace_id: Optional[str],
        initiative_id: Optional[str],
        parent_id: Optional[str] = None,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        if entity_type not in ENTITY_TYPES:
            raise RepositoryError(f"unsupported entity type: {entity_type}")
        entity_id = str(document.get("id") or "")
        if not entity_id:
            raise RepositoryError(f"{entity_type} document requires id")
        existing = self.connection.execute(
            "SELECT revision, archived_at, created_at FROM repository_entities WHERE entity_type=? AND entity_id=?",
            (entity_type, entity_id),
        ).fetchone()
        now = utc_now()
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and expected_revision != actual:
                raise OptimisticConcurrencyError(entity_type, entity_id, expected_revision, actual)
            revision = actual + 1
            self.connection.execute(
                """UPDATE repository_entities SET workspace_id=?, initiative_id=?, parent_id=?,
                   name=?, lifecycle_status=?, revision=?, updated_at=?, document_json=?
                   WHERE entity_type=? AND entity_id=?""",
                (
                    workspace_id, initiative_id, parent_id, self._entity_name(entity_type, document),
                    str(document.get("status") or document.get("lifecycle_status") or "draft"),
                    revision, now, canonical_json(document), entity_type, entity_id,
                ),
            )
            action = "update"
        else:
            revision = 1
            self.connection.execute(
                """INSERT INTO repository_entities(
                    entity_type, entity_id, workspace_id, initiative_id, parent_id, name,
                    lifecycle_status, revision, created_at, updated_at, document_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entity_type, entity_id, workspace_id, initiative_id, parent_id,
                    self._entity_name(entity_type, document),
                    str(document.get("status") or document.get("lifecycle_status") or "draft"),
                    revision, str(document.get("created_at") or now), now, canonical_json(document),
                ),
            )
            action = "create"
        self._audit(action, entity_type, entity_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor)
        row = self.get_entity(entity_type, entity_id, include_archived=True)
        return row

    def get_entity(self, entity_type: str, entity_id: str, *, include_archived: bool = False) -> Dict[str, Any]:
        query = "SELECT * FROM repository_entities WHERE entity_type=? AND entity_id=?"
        params: List[Any] = [entity_type, entity_id]
        if not include_archived:
            query += " AND archived_at IS NULL"
        row = self.connection.execute(query, params).fetchone()
        if not row:
            raise NotFoundError(f"{entity_type} not found: {entity_id}")
        result = dict(row)
        result["document"] = json.loads(result.pop("document_json"))
        return result

    def update_entity(
        self,
        entity_type: str,
        entity_id: str,
        changes: Dict[str, Any],
        *,
        expected_revision: int,
        actor: str = "system",
    ) -> Dict[str, Any]:
        current = self.get_entity(entity_type, entity_id, include_archived=True)
        document = dict(current["document"])
        document.update(changes)
        return self.upsert_entity(
            entity_type, document,
            workspace_id=current["workspace_id"], initiative_id=current["initiative_id"],
            parent_id=current["parent_id"], expected_revision=expected_revision, actor=actor,
        )

    def delete_entity(self, entity_type: str, entity_id: str, *, expected_revision: int, actor: str = "system") -> None:
        current = self.get_entity(entity_type, entity_id, include_archived=True)
        if int(current["revision"]) != expected_revision:
            raise OptimisticConcurrencyError(entity_type, entity_id, expected_revision, int(current["revision"]))
        self.connection.execute(
            "DELETE FROM repository_entities WHERE entity_type=? AND entity_id=?", (entity_type, entity_id)
        )
        self._audit("delete", entity_type, entity_id, workspace_id=current["workspace_id"], initiative_id=current["initiative_id"], revision=expected_revision, actor=actor)
        self.connection.commit()

    def list_entities(
        self,
        entity_type: str,
        *,
        workspace_id: Optional[str] = None,
        initiative_id: Optional[str] = None,
        search: str = "",
        lifecycle_status: Optional[str] = None,
        include_archived: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        clauses = ["entity_type=?"]
        params: List[Any] = [entity_type]
        if workspace_id:
            clauses.append("workspace_id=?")
            params.append(workspace_id)
        if initiative_id:
            clauses.append("initiative_id=?")
            params.append(initiative_id)
        if search:
            clauses.append("LOWER(name) LIKE ?")
            params.append(f"%{search.casefold()}%")
        if lifecycle_status:
            clauses.append("lifecycle_status=?")
            params.append(lifecycle_status)
        if not include_archived:
            clauses.append("archived_at IS NULL")
        params.extend([max(1, min(limit, 500)), max(0, offset)])
        rows = self.connection.execute(
            f"SELECT * FROM repository_entities WHERE {' AND '.join(clauses)} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["document"] = json.loads(item.pop("document_json"))
            results.append(item)
        return results

    def archive_entity(self, entity_type: str, entity_id: str, *, expected_revision: int, actor: str = "system") -> Dict[str, Any]:
        current = self.get_entity(entity_type, entity_id, include_archived=True)
        actual = int(current["revision"])
        if actual != expected_revision:
            raise OptimisticConcurrencyError(entity_type, entity_id, expected_revision, actual)
        now = utc_now()
        self.connection.execute(
            "UPDATE repository_entities SET archived_at=?, revision=?, updated_at=? WHERE entity_type=? AND entity_id=?",
            (now, actual + 1, now, entity_type, entity_id),
        )
        self._audit("archive", entity_type, entity_id, workspace_id=current["workspace_id"], initiative_id=current["initiative_id"], revision=actual + 1, actor=actor)
        self.connection.commit()
        return self.get_entity(entity_type, entity_id, include_archived=True)

    def restore_entity(self, entity_type: str, entity_id: str, *, expected_revision: int, actor: str = "system") -> Dict[str, Any]:
        current = self.get_entity(entity_type, entity_id, include_archived=True)
        actual = int(current["revision"])
        if actual != expected_revision:
            raise OptimisticConcurrencyError(entity_type, entity_id, expected_revision, actual)
        now = utc_now()
        self.connection.execute(
            "UPDATE repository_entities SET archived_at=NULL, revision=?, updated_at=? WHERE entity_type=? AND entity_id=?",
            (actual + 1, now, entity_type, entity_id),
        )
        self._audit("restore", entity_type, entity_id, workspace_id=current["workspace_id"], initiative_id=current["initiative_id"], revision=actual + 1, actor=actor)
        self.connection.commit()
        return self.get_entity(entity_type, entity_id)

    @staticmethod
    def _contract_entities(contract: Dict[str, Any]) -> Iterable[tuple[str, Dict[str, Any], Optional[str]]]:
        facts = contract["facts"]
        measurement = facts["measurement"]
        yield "workspace", facts["workspace"], None
        yield "initiative", facts["initiative"], facts["workspace"]["id"]
        yield "goal", facts["goal"], facts["initiative"]["id"]
        yield "indicator", facts["indicator"], facts["outcomes"][0]["id"]
        yield "target", measurement["target"], facts["indicator"]["id"]
        for observation in measurement.get("observations", []):
            yield "observation", observation, facts["indicator"]["id"]
        for source in facts.get("sources", []):
            yield "source", source, facts["initiative"]["id"]

    def save_contract(
        self,
        contract: Dict[str, Any],
        *,
        expected_revision: Optional[int] = None,
        save_state: str = "saved",
        actor: str = "system",
    ) -> Dict[str, Any]:
        if save_state not in SAVE_STATES:
            raise RepositoryError(f"invalid save state: {save_state}")
        facts = contract.get("facts") or {}
        workspace = facts.get("workspace") or {}
        initiative = facts.get("initiative") or {}
        record_id = str(contract.get("record_id") or "")
        workspace_id = str(workspace.get("id") or "")
        initiative_id = str(initiative.get("id") or "")
        if not record_id or not workspace_id or not initiative_id:
            raise RepositoryError("canonical contract requires record, workspace, and initiative identifiers")
        now = utc_now()
        digest = content_hash(contract)
        with self.transaction():
            existing = self.connection.execute(
                "SELECT revision, created_at, content_hash FROM canonical_contracts WHERE record_id=?", (record_id,)
            ).fetchone()
            previous_content_hash = str(existing["content_hash"]) if existing else None
            if existing:
                actual = int(existing["revision"])
                if expected_revision is not None and expected_revision != actual:
                    raise OptimisticConcurrencyError("contract", record_id, expected_revision, actual)
                revision = actual + 1
                self.connection.execute(
                    """UPDATE canonical_contracts SET workspace_id=?, initiative_id=?, contract_version=?,
                       save_state=?, lifecycle_status=?, revision=?, content_hash=?, updated_at=?, contract_json=?
                       WHERE record_id=?""",
                    (
                        workspace_id, initiative_id, str(contract.get("contract_version") or ""), save_state,
                        str(contract.get("lifecycle_status") or "draft"), revision, digest, now,
                        canonical_json(contract), record_id,
                    ),
                )
                action = "save"
            else:
                if expected_revision not in (None, 0):
                    raise OptimisticConcurrencyError("contract", record_id, int(expected_revision), 0)
                revision = 1
                self.connection.execute(
                    """INSERT INTO canonical_contracts(record_id, workspace_id, initiative_id,
                       contract_version, save_state, lifecycle_status, revision, content_hash,
                       created_at, updated_at, contract_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        record_id, workspace_id, initiative_id, str(contract.get("contract_version") or ""),
                        save_state, str(contract.get("lifecycle_status") or "draft"), revision, digest,
                        str(contract.get("created_at") or now), now, canonical_json(contract),
                    ),
                )
                action = "create"
            for entity_type, document, parent_id in self._contract_entities(contract):
                projection = dict(document)
                if entity_type in {"workspace", "initiative"}:
                    projection["lifecycle_status"] = str(contract.get("lifecycle_status") or "draft")
                self.upsert_entity(
                    entity_type, projection, workspace_id=workspace_id, initiative_id=initiative_id,
                    parent_id=parent_id, actor=actor,
                )
            self._materialize_contract_evidence(contract, actor=actor)
            self._materialize_contract_registry(contract, actor=actor)
            self._materialize_contract_measurement(contract, actor=actor)
            self._materialize_contract_workflow(
                contract, repository_revision=revision, previous_content_hash=previous_content_hash,
                action=action, actor=actor,
            )
            self.connection.execute("DELETE FROM draft_autosaves WHERE initiative_id=?", (initiative_id,))
            self._audit(action, "contract", record_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor, details={"save_state": save_state, "content_hash": digest})
        return self.get_contract(record_id=record_id)

    def get_contract(self, *, record_id: Optional[str] = None, initiative_id: Optional[str] = None) -> Dict[str, Any]:
        if not record_id and not initiative_id:
            raise RepositoryError("record_id or initiative_id is required")
        field, value = ("record_id", record_id) if record_id else ("initiative_id", initiative_id)
        row = self.connection.execute(f"SELECT * FROM canonical_contracts WHERE {field}=?", (value,)).fetchone()
        if not row:
            raise NotFoundError(f"contract not found for {field}={value}")
        result = dict(row)
        result["contract"] = json.loads(result.pop("contract_json"))
        return result

    def autosave_contract(self, contract: Dict[str, Any], *, base_revision: int, actor: str = "system") -> Dict[str, Any]:
        initiative_id = contract["facts"]["initiative"]["id"]
        record_id = contract["record_id"]
        try:
            current = self.get_contract(record_id=record_id)
            actual = int(current["revision"])
        except NotFoundError:
            actual = 0
        if base_revision != actual:
            raise OptimisticConcurrencyError("contract", record_id, base_revision, actual)
        now = utc_now()
        digest = content_hash(contract)
        self.connection.execute(
            """INSERT INTO draft_autosaves(initiative_id, base_revision, content_hash, saved_at, contract_json)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(initiative_id) DO UPDATE SET base_revision=excluded.base_revision,
               content_hash=excluded.content_hash, saved_at=excluded.saved_at, contract_json=excluded.contract_json""",
            (initiative_id, base_revision, digest, now, canonical_json(contract)),
        )
        self._audit("autosave", "contract", record_id, workspace_id=contract["facts"]["workspace"]["id"], initiative_id=initiative_id, revision=base_revision, actor=actor, details={"content_hash": digest})
        self.connection.commit()
        return {"initiative_id": initiative_id, "base_revision": base_revision, "content_hash": digest, "saved_at": now, "contract": contract}

    def get_autosave(self, initiative_id: str) -> Optional[Dict[str, Any]]:
        row = self.connection.execute("SELECT * FROM draft_autosaves WHERE initiative_id=?", (initiative_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["contract"] = json.loads(result.pop("contract_json"))
        return result

    def create_portfolio(self, portfolio_id: str, workspace_id: str, name: str, description: str = "", *, actor: str = "system") -> Dict[str, Any]:
        now = utc_now()
        self.connection.execute(
            "INSERT INTO portfolios(portfolio_id, workspace_id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (portfolio_id, workspace_id, name.strip(), description.strip(), now, now),
        )
        self._audit("create", "portfolio", portfolio_id, workspace_id=workspace_id, revision=1, actor=actor)
        self.connection.commit()
        return self.get_portfolio(portfolio_id)

    def get_portfolio(self, portfolio_id: str, *, include_archived: bool = False) -> Dict[str, Any]:
        query = "SELECT * FROM portfolios WHERE portfolio_id=?"
        if not include_archived:
            query += " AND archived_at IS NULL"
        row = self.connection.execute(query, (portfolio_id,)).fetchone()
        if not row:
            raise NotFoundError(f"portfolio not found: {portfolio_id}")
        result = dict(row)
        result["initiative_ids"] = [
            item["initiative_id"] for item in self.connection.execute(
                "SELECT initiative_id FROM portfolio_memberships WHERE portfolio_id=? ORDER BY position, added_at",
                (portfolio_id,),
            )
        ]
        return result

    def list_portfolios(self, workspace_id: str, *, search: str = "", include_archived: bool = False) -> List[Dict[str, Any]]:
        clauses = ["workspace_id=?"]
        params: List[Any] = [workspace_id]
        if search:
            clauses.append("LOWER(name) LIKE ?")
            params.append(f"%{search.casefold()}%")
        if not include_archived:
            clauses.append("archived_at IS NULL")
        ids = [row["portfolio_id"] for row in self.connection.execute(
            f"SELECT portfolio_id FROM portfolios WHERE {' AND '.join(clauses)} ORDER BY name", params
        )]
        return [self.get_portfolio(portfolio_id, include_archived=True) for portfolio_id in ids]

    def add_to_portfolio(self, portfolio_id: str, initiative_id: str, *, position: int = 0, actor: str = "system") -> Dict[str, Any]:
        portfolio = self.get_portfolio(portfolio_id)
        self.get_entity("initiative", initiative_id, include_archived=True)
        self.connection.execute(
            "INSERT OR IGNORE INTO portfolio_memberships(portfolio_id, initiative_id, position, added_at) VALUES (?, ?, ?, ?)",
            (portfolio_id, initiative_id, int(position), utc_now()),
        )
        self._audit("add_member", "portfolio", portfolio_id, workspace_id=portfolio["workspace_id"], initiative_id=initiative_id, revision=portfolio["revision"], actor=actor)
        self.connection.commit()
        return self.get_portfolio(portfolio_id)

    def remove_from_portfolio(self, portfolio_id: str, initiative_id: str, *, actor: str = "system") -> Dict[str, Any]:
        portfolio = self.get_portfolio(portfolio_id)
        self.connection.execute(
            "DELETE FROM portfolio_memberships WHERE portfolio_id=? AND initiative_id=?", (portfolio_id, initiative_id)
        )
        self._audit("remove_member", "portfolio", portfolio_id, workspace_id=portfolio["workspace_id"], initiative_id=initiative_id, revision=portfolio["revision"], actor=actor)
        self.connection.commit()
        return self.get_portfolio(portfolio_id)

    def record_import(
        self,
        original_document: Dict[str, Any],
        canonical_contract: Dict[str, Any],
        *,
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ImportResult:
        original_hash = content_hash(original_document)
        existing = self.connection.execute("SELECT * FROM import_records WHERE content_hash=?", (original_hash,)).fetchone()
        if existing:
            contract = self.get_contract(record_id=existing["record_id"])
            return ImportResult(existing["import_id"], existing["record_id"], existing["initiative_id"], "unchanged", original_hash, int(contract["revision"]))
        try:
            stored = self.get_contract(record_id=canonical_contract["record_id"])
            if stored["content_hash"] == content_hash(canonical_contract):
                import_status = "unchanged"
            else:
                stored = self.save_contract(canonical_contract, expected_revision=int(stored["revision"]), save_state="saved", actor=actor)
                import_status = "updated"
        except NotFoundError:
            stored = self.save_contract(canonical_contract, save_state="saved", actor=actor)
            import_status = "imported"
        source_version = str(original_document.get("contract_version") or original_document.get("schema_version") or "1.0.x")
        import_id = f"gic-import-{original_hash[:20]}"
        self.connection.execute(
            """INSERT INTO import_records(import_id, content_hash, source_contract_version,
               record_id, initiative_id, status, imported_at, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                import_id, original_hash, source_version, canonical_contract["record_id"],
                canonical_contract["facts"]["initiative"]["id"], import_status, utc_now(),
                canonical_json(metadata or {}),
            ),
        )
        self._audit("import", "contract", canonical_contract["record_id"], workspace_id=canonical_contract["facts"]["workspace"]["id"], initiative_id=canonical_contract["facts"]["initiative"]["id"], revision=int(stored["revision"]), actor=actor, details={"import_id": import_id, "source_contract_version": source_version, "content_hash": original_hash, "status": import_status})
        self.connection.commit()
        return ImportResult(import_id, canonical_contract["record_id"], canonical_contract["facts"]["initiative"]["id"], import_status, original_hash, int(stored["revision"]))

    @staticmethod
    def _decode_row(row: sqlite3.Row | Dict[str, Any], *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            if field in item:
                item[field.removesuffix("_json")] = json.loads(item.pop(field) or "{}")
        return item

    def register_source(
        self,
        source: Dict[str, Any],
        *,
        workspace_id: str,
        initiative_id: Optional[str] = None,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        source_id = str(source.get("source_id") or source.get("id") or repository_id("source", workspace_id, initiative_id or "", source.get("title", ""), source.get("locator", "")))
        title = str(source.get("title") or "").strip()
        if not title:
            raise RepositoryError("source title is required")
        now = utc_now()
        metadata = dict(source.get("metadata") or {})
        values = {
            "source_id": source_id, "workspace_id": workspace_id, "initiative_id": initiative_id,
            "title": title, "source_type": str(source.get("source_type") or "document"),
            "locator": str(source.get("locator") or ""), "creator": str(source.get("creator") or ""),
            "publisher": str(source.get("publisher") or ""), "published_at": source.get("published_at"),
            "retrieved_at": source.get("retrieved_at"), "url": str(source.get("url") or ""),
            "doi": str(source.get("doi") or ""), "license": str(source.get("license") or "not_recorded"),
            "access_rights": str(source.get("access_rights") or "not_recorded"),
            "lifecycle_status": str(source.get("lifecycle_status") or "active"), "metadata_json": canonical_json(metadata),
        }
        with self.transaction():
            current = self.connection.execute("SELECT * FROM source_records WHERE source_id=?", (source_id,)).fetchone()
            if current:
                actual = int(current["revision"])
                if expected_revision is not None and expected_revision != actual:
                    raise OptimisticConcurrencyError("source", source_id, expected_revision, actual)
                revision = actual + 1
                self.connection.execute(
                    """UPDATE source_records SET workspace_id=?,initiative_id=?,title=?,source_type=?,locator=?,creator=?,publisher=?,published_at=?,retrieved_at=?,url=?,doi=?,license=?,access_rights=?,lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE source_id=?""",
                    (values["workspace_id"], values["initiative_id"], values["title"], values["source_type"], values["locator"], values["creator"], values["publisher"], values["published_at"], values["retrieved_at"], values["url"], values["doi"], values["license"], values["access_rights"], values["lifecycle_status"], revision, now, values["metadata_json"], source_id),
                )
                action = "update_source"
            else:
                if expected_revision not in (None, 0):
                    raise OptimisticConcurrencyError("source", source_id, int(expected_revision), 0)
                revision = 1
                self.connection.execute(
                    """INSERT INTO source_records(source_id,workspace_id,initiative_id,title,source_type,locator,creator,publisher,published_at,retrieved_at,url,doi,license,access_rights,lifecycle_status,current_version,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (source_id, values["workspace_id"], values["initiative_id"], values["title"], values["source_type"], values["locator"], values["creator"], values["publisher"], values["published_at"], values["retrieved_at"], values["url"], values["doi"], values["license"], values["access_rights"], values["lifecycle_status"], 0, revision, str(source.get("created_at") or now), now, values["metadata_json"]),
                )
                action = "create_source"
            self._audit(action, "source", source_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor)
        return self.get_source(source_id)

    def get_source(self, source_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM source_records WHERE source_id=?", (source_id,)).fetchone()
        if not row:
            raise NotFoundError(f"source not found: {source_id}")
        item = self._decode_row(row, "metadata_json")
        item["versions"] = [self._decode_row(version, "metadata_json") for version in self.connection.execute("SELECT * FROM source_versions WHERE source_id=? ORDER BY version_number", (source_id,)).fetchall()]
        return item

    def list_sources(self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None, search: str = "", limit: int = 200) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        if workspace_id:
            clauses.append("workspace_id=?"); params.append(workspace_id)
        if initiative_id:
            clauses.append("initiative_id=?"); params.append(initiative_id)
        if search:
            clauses.append("(LOWER(title) LIKE ? OR LOWER(locator) LIKE ? OR LOWER(doi) LIKE ?)")
            like = f"%{search.casefold()}%"; params.extend([like, like, like])
        params.append(max(1, min(limit, 500)))
        return [self._decode_row(row, "metadata_json") for row in self.connection.execute(f"SELECT * FROM source_records WHERE {' AND '.join(clauses)} ORDER BY updated_at DESC LIMIT ?", params).fetchall()]

    def add_source_version(
        self,
        source_id: str,
        *,
        version_label: str = "",
        payload: bytes | str | None = None,
        checksum_algorithm: str = "sha256",
        checksum_value: str = "",
        mime_type: str = "application/octet-stream",
        size_bytes: Optional[int] = None,
        captured_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        source = self.get_source(source_id)
        if checksum_algorithm not in CHECKSUM_ALGORITHMS:
            raise RepositoryError(f"unsupported checksum algorithm: {checksum_algorithm}")
        calculated = checksum_payload(payload, checksum_algorithm) if payload is not None else ""
        if checksum_value and calculated and checksum_value.lower() != calculated:
            raise RepositoryError("provided checksum does not match source payload")
        checksum = (checksum_value or calculated or content_hash({"source_id": source_id, "version_label": version_label, "metadata": metadata or {}})).lower()
        existing = self.connection.execute("SELECT * FROM source_versions WHERE source_id=? AND checksum_algorithm=? AND checksum_value=?", (source_id, checksum_algorithm, checksum)).fetchone()
        if existing:
            return self._decode_row(existing, "metadata_json")
        with self.transaction():
            number = int(self.connection.execute("SELECT COALESCE(MAX(version_number),0)+1 AS number FROM source_versions WHERE source_id=?", (source_id,)).fetchone()["number"])
            source_version_id = repository_id("source-version", source_id, number, checksum)
            self.connection.execute(
                """INSERT INTO source_versions(source_version_id,source_id,version_number,version_label,content_hash,checksum_algorithm,checksum_value,mime_type,size_bytes,captured_at,captured_by,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (source_version_id, source_id, number, version_label or str(number), calculated or checksum, checksum_algorithm, checksum, mime_type, size_bytes if size_bytes is not None else (len(payload) if isinstance(payload, bytes) else len(payload.encode("utf-8")) if isinstance(payload, str) else None), utc_now(), captured_by, canonical_json(metadata or {})),
            )
            self.connection.execute("UPDATE source_records SET current_version=?,updated_at=? WHERE source_id=?", (number, utc_now(), source_id))
            self._audit("add_source_version", "source", source_id, workspace_id=source["workspace_id"], initiative_id=source["initiative_id"], revision=source["revision"], actor=captured_by, details={"source_version_id": source_version_id, "checksum": checksum})
        return self._decode_row(self.connection.execute("SELECT * FROM source_versions WHERE source_version_id=?", (source_version_id,)).fetchone(), "metadata_json")

    def capture_evidence(
        self,
        source_id: str,
        *,
        evidence_type: str = "excerpt",
        title: str = "",
        locator: str = "",
        exact_quote: str = "",
        paraphrase: str = "",
        notes: str = "",
        source_version_id: Optional[str] = None,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None,
        character_start: Optional[int] = None,
        character_end: Optional[int] = None,
        captured_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        evidence_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if evidence_type not in EVIDENCE_TYPES:
            raise RepositoryError(f"unsupported evidence type: {evidence_type}")
        if not any(str(value).strip() for value in (exact_quote, paraphrase, notes)):
            raise RepositoryError("evidence requires an exact quote, paraphrase, or note")
        source = self.get_source(source_id)
        if source_version_id is None and source.get("versions"):
            source_version_id = source["versions"][-1]["source_version_id"]
        payload = {"source_id": source_id, "source_version_id": source_version_id, "evidence_type": evidence_type, "locator": locator, "exact_quote": exact_quote, "paraphrase": paraphrase, "notes": notes, "page_start": page_start, "page_end": page_end, "character_start": character_start, "character_end": character_end}
        digest = content_hash(payload)
        evidence_id = evidence_id or repository_id("evidence", source_id, digest)
        now = utc_now()
        with self.transaction():
            existing = self.connection.execute("SELECT revision FROM evidence_items WHERE evidence_id=?", (evidence_id,)).fetchone()
            revision = int(existing["revision"]) + 1 if existing else 1
            self.connection.execute(
                """INSERT INTO evidence_items(evidence_id,source_id,source_version_id,workspace_id,initiative_id,evidence_type,title,locator,exact_quote,paraphrase,notes,page_start,page_end,character_start,character_end,captured_at,captured_by,content_hash,archived_at,revision,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(evidence_id) DO UPDATE SET source_version_id=excluded.source_version_id,evidence_type=excluded.evidence_type,title=excluded.title,locator=excluded.locator,exact_quote=excluded.exact_quote,paraphrase=excluded.paraphrase,notes=excluded.notes,page_start=excluded.page_start,page_end=excluded.page_end,character_start=excluded.character_start,character_end=excluded.character_end,captured_at=excluded.captured_at,captured_by=excluded.captured_by,content_hash=excluded.content_hash,revision=excluded.revision,metadata_json=excluded.metadata_json""",
                (evidence_id, source_id, source_version_id, source["workspace_id"], source["initiative_id"], evidence_type, title, locator, exact_quote, paraphrase, notes, page_start, page_end, character_start, character_end, now, captured_by, digest, None, revision, canonical_json(metadata or {})),
            )
            self._audit("capture_evidence", "evidence", evidence_id, workspace_id=source["workspace_id"], initiative_id=source["initiative_id"], revision=revision, actor=captured_by, details={"source_id": source_id, "source_version_id": source_version_id})
        return self.get_evidence(evidence_id)

    def get_evidence(self, evidence_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM evidence_items WHERE evidence_id=?", (evidence_id,)).fetchone()
        if not row:
            raise NotFoundError(f"evidence not found: {evidence_id}")
        return self._decode_row(row, "metadata_json")

    def register_dataset(self, source_id: str, dataset: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        source = self.get_source(source_id)
        title = str(dataset.get("title") or "").strip()
        if not title:
            raise RepositoryError("dataset title is required")
        checksum_algorithm = str(dataset.get("checksum_algorithm") or "sha256")
        if checksum_algorithm not in CHECKSUM_ALGORITHMS:
            raise RepositoryError(f"unsupported checksum algorithm: {checksum_algorithm}")
        checksum = str(dataset.get("checksum_value") or content_hash(dataset)).lower()
        dataset_id = str(dataset.get("dataset_id") or repository_id("dataset", source_id, title, dataset.get("version", ""), checksum))
        now = utc_now()
        values = (dataset_id, source_id, dataset.get("source_version_id"), source["workspace_id"], source["initiative_id"], title, str(dataset.get("version") or ""), str(dataset.get("description") or ""), str(dataset.get("landing_page") or ""), str(dataset.get("distribution_url") or ""), str(dataset.get("license") or source.get("license") or "not_recorded"), checksum_algorithm, checksum, str(dataset.get("schema_fingerprint") or ""), str(dataset.get("temporal_coverage") or ""), str(dataset.get("spatial_coverage") or ""), dataset.get("row_count"), dataset.get("column_count"), now, now, canonical_json(dataset.get("metadata") or {}))
        with self.transaction():
            self.connection.execute("""INSERT INTO datasets(dataset_id,source_id,source_version_id,workspace_id,initiative_id,title,version,description,landing_page,distribution_url,license,checksum_algorithm,checksum_value,schema_fingerprint,temporal_coverage,spatial_coverage,row_count,column_count,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(dataset_id) DO UPDATE SET source_version_id=excluded.source_version_id,title=excluded.title,version=excluded.version,description=excluded.description,landing_page=excluded.landing_page,distribution_url=excluded.distribution_url,license=excluded.license,checksum_algorithm=excluded.checksum_algorithm,checksum_value=excluded.checksum_value,schema_fingerprint=excluded.schema_fingerprint,temporal_coverage=excluded.temporal_coverage,spatial_coverage=excluded.spatial_coverage,row_count=excluded.row_count,column_count=excluded.column_count,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""", values)
            self._audit("register_dataset", "dataset", dataset_id, workspace_id=source["workspace_id"], initiative_id=source["initiative_id"], actor=actor, details={"source_id": source_id, "checksum": checksum})
        return self._decode_row(self.connection.execute("SELECT * FROM datasets WHERE dataset_id=?", (dataset_id,)).fetchone(), "metadata_json")

    def add_provenance_edge(self, *, workspace_id: str, initiative_id: Optional[str], subject_type: str, subject_id: str, predicate: str, object_type: str, object_id: str, process_name: str = "", method_id: Optional[str] = None, method_version: str = "", occurred_at: Optional[str] = None, actor: str = "system", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        edge_id = repository_id("edge", subject_type, subject_id, predicate, object_type, object_id, method_id or "")
        self.connection.execute("""INSERT INTO provenance_edges(edge_id,workspace_id,initiative_id,subject_type,subject_id,predicate,object_type,object_id,process_name,method_id,method_version,occurred_at,actor,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(edge_id) DO UPDATE SET process_name=excluded.process_name,method_version=excluded.method_version,occurred_at=excluded.occurred_at,actor=excluded.actor,metadata_json=excluded.metadata_json""", (edge_id, workspace_id, initiative_id, subject_type, subject_id, predicate, object_type, object_id, process_name, method_id, method_version, occurred_at or utc_now(), actor, canonical_json(metadata or {})))
        return self._decode_row(self.connection.execute("SELECT * FROM provenance_edges WHERE edge_id=?", (edge_id,)).fetchone(), "metadata_json")

    def link_claim_evidence(self, claim_id: str, evidence_id: str, *, relationship: str = "supports", strength: str = "direct", notes: str = "", linked_by: str = "system") -> Dict[str, Any]:
        if relationship not in CLAIM_EVIDENCE_RELATIONSHIPS:
            raise RepositoryError(f"unsupported claim-evidence relationship: {relationship}")
        if strength not in EVIDENCE_STRENGTHS:
            raise RepositoryError(f"unsupported evidence strength: {strength}")
        evidence = self.get_evidence(evidence_id)
        with self.transaction():
            self.connection.execute("""INSERT INTO claim_evidence_links(claim_id,evidence_id,relationship,strength,notes,linked_at,linked_by) VALUES (?,?,?,?,?,?,?) ON CONFLICT(claim_id,evidence_id,relationship) DO UPDATE SET strength=excluded.strength,notes=excluded.notes,linked_at=excluded.linked_at,linked_by=excluded.linked_by""", (claim_id, evidence_id, relationship, strength, notes, utc_now(), linked_by))
            self._audit("link_claim_evidence", "claim", claim_id, workspace_id=evidence["workspace_id"], initiative_id=evidence["initiative_id"], actor=linked_by, details={"evidence_id": evidence_id, "relationship": relationship, "strength": strength})
        return dict(self.connection.execute("SELECT * FROM claim_evidence_links WHERE claim_id=? AND evidence_id=? AND relationship=?", (claim_id, evidence_id, relationship)).fetchone())

    def _materialize_contract_evidence(self, contract: Dict[str, Any], *, actor: str) -> None:
        facts = contract["facts"]
        workspace_id = facts["workspace"]["id"]
        initiative_id = facts["initiative"]["id"]
        now = utc_now()
        methods = {item["id"]: item for item in facts.get("methods", [])}
        sources = {item["id"]: item for item in facts.get("sources", [])}
        for source_id, source in sources.items():
            existing = self.connection.execute("SELECT * FROM source_records WHERE source_id=?", (source_id,)).fetchone()
            metadata = canonical_json({"canonical_entity": source})
            if not existing:
                self.connection.execute("""INSERT INTO source_records(source_id,workspace_id,initiative_id,title,source_type,locator,creator,publisher,published_at,retrieved_at,url,doi,license,access_rights,lifecycle_status,current_version,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (source_id, workspace_id, initiative_id, str(source.get("title") or "Untitled source"), str(source.get("source_type") or "entered_source"), str(source.get("locator") or ""), "", "", None, None, "", "", "not_recorded", "not_recorded", "active", 0, 1, str(source.get("created_at") or now), now, metadata))
            source_digest = content_hash(source)
            version = self.connection.execute("SELECT * FROM source_versions WHERE source_id=? AND checksum_value=?", (source_id, source_digest)).fetchone()
            if not version:
                number = int(self.connection.execute("SELECT COALESCE(MAX(version_number),0)+1 AS number FROM source_versions WHERE source_id=?", (source_id,)).fetchone()["number"])
                version_id = repository_id("source-version", source_id, number, source_digest)
                self.connection.execute("""INSERT INTO source_versions(source_version_id,source_id,version_number,version_label,content_hash,checksum_algorithm,checksum_value,mime_type,size_bytes,captured_at,captured_by,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (version_id, source_id, number, f"contract-{contract.get('contract_version','')}", source_digest, "sha256", source_digest, "application/vnd.global-impact-catalyst.source+json", len(canonical_json(source).encode("utf-8")), now, actor, canonical_json({"record_id": contract["record_id"]})))
                self.connection.execute("UPDATE source_records SET current_version=?,updated_at=? WHERE source_id=?", (number, now, source_id))
        measurement = facts.get("measurement") or {}
        measurement_records = [measurement.get("baseline"), *(measurement.get("observations") or [])]
        for item in [record for record in measurement_records if record]:
            for source_id in item.get("source_ids", []):
                if source_id in sources:
                    self.add_provenance_edge(workspace_id=workspace_id, initiative_id=initiative_id, subject_type="source", subject_id=source_id, predicate="supports", object_type=item["entity_type"], object_id=item["id"], process_name="canonical contract materialization", method_id=item.get("method_id"), method_version=str(methods.get(item.get("method_id"), {}).get("version") or ""), occurred_at=str(item.get("updated_at") or now), actor=actor)
            if item.get("method_id"):
                method = methods.get(item["method_id"], {})
                self.add_provenance_edge(workspace_id=workspace_id, initiative_id=initiative_id, subject_type="method", subject_id=item["method_id"], predicate="produced", object_type=item["entity_type"], object_id=item["id"], process_name=str(method.get("name") or "measurement method"), method_id=item["method_id"], method_version=str(method.get("version") or ""), occurred_at=str(item.get("updated_at") or now), actor=actor)
        for claim in contract.get("derived", {}).get("claims", []):
            for reference in claim.get("evidence_refs", []):
                ref_type = "entity"
                for candidate in ("source", "method", "baseline", "observation", "target"):
                    if reference.startswith(f"gic-{candidate}-"):
                        ref_type = candidate; break
                self.add_provenance_edge(workspace_id=workspace_id, initiative_id=initiative_id, subject_type=ref_type, subject_id=reference, predicate="informs_claim", object_type="claim", object_id=claim["id"], process_name="claim evidence declaration", occurred_at=str(claim.get("updated_at") or now), actor=actor)

    def evidence_chain(self, initiative_id: str) -> Dict[str, Any]:
        contract = self.get_contract(initiative_id=initiative_id)
        workspace_id = contract["workspace_id"]
        sources = [self.get_source(row["source_id"]) for row in self.connection.execute("SELECT source_id FROM source_records WHERE initiative_id=? ORDER BY title", (initiative_id,)).fetchall()]
        evidence = [self._decode_row(row, "metadata_json") for row in self.connection.execute("SELECT * FROM evidence_items WHERE initiative_id=? ORDER BY captured_at", (initiative_id,)).fetchall()]
        datasets = [self._decode_row(row, "metadata_json") for row in self.connection.execute("SELECT * FROM datasets WHERE initiative_id=? ORDER BY title", (initiative_id,)).fetchall()]
        edges = [self._decode_row(row, "metadata_json") for row in self.connection.execute("SELECT * FROM provenance_edges WHERE initiative_id=? ORDER BY occurred_at,edge_id", (initiative_id,)).fetchall()]
        evidence_ids = {item["evidence_id"] for item in evidence}
        links = [dict(row) for row in self.connection.execute("SELECT l.* FROM claim_evidence_links l JOIN evidence_items e ON e.evidence_id=l.evidence_id WHERE e.initiative_id=? ORDER BY l.linked_at", (initiative_id,)).fetchall()]
        claim_ids = {claim["id"] for claim in contract["contract"].get("derived", {}).get("claims", [])}
        missing_checksums = [source["source_id"] for source in sources if not source.get("versions")]
        orphan_links = [link for link in links if link["evidence_id"] not in evidence_ids or link["claim_id"] not in claim_ids]
        contradictions = [link for link in links if link["relationship"] == "contradicts"]
        return {"chain_type": "global_impact_evidence_chain", "chain_version": "1.3.0", "workspace_id": workspace_id, "initiative_id": initiative_id, "generated_at": utc_now(), "sources": sources, "evidence_items": evidence, "datasets": datasets, "provenance_edges": edges, "claim_evidence_links": links, "integrity": {"valid": not missing_checksums and not orphan_links, "source_count": len(sources), "version_count": sum(len(source.get("versions", [])) for source in sources), "evidence_count": len(evidence), "dataset_count": len(datasets), "edge_count": len(edges), "claim_link_count": len(links), "missing_checksum_source_ids": missing_checksums, "orphan_claim_evidence_links": orphan_links, "contradicting_link_count": len(contradictions)}}

    def export_evidence_repository(self, workspace_id: str) -> Dict[str, Any]:
        def rows(table: str, where: str = "workspace_id=?") -> List[Dict[str, Any]]:
            return [self._decode_row(row, "metadata_json") for row in self.connection.execute(f"SELECT * FROM {table} WHERE {where} ORDER BY 1", (workspace_id,)).fetchall()]
        sources = rows("source_records")
        source_ids = [source["source_id"] for source in sources]
        versions: List[Dict[str, Any]] = []
        links: List[Dict[str, Any]] = []
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            versions = [self._decode_row(row, "metadata_json") for row in self.connection.execute(f"SELECT * FROM source_versions WHERE source_id IN ({placeholders}) ORDER BY source_id,version_number", source_ids).fetchall()]
            links = [dict(row) for row in self.connection.execute(f"SELECT l.* FROM claim_evidence_links l JOIN evidence_items e ON e.evidence_id=l.evidence_id WHERE e.workspace_id=? ORDER BY l.claim_id,l.evidence_id", (workspace_id,)).fetchall()]
        return {"repository_type": "global_impact_evidence_repository", "repository_version": "1.3.0", "workspace_id": workspace_id, "sources": sources, "source_versions": versions, "evidence_items": rows("evidence_items"), "datasets": rows("datasets"), "provenance_edges": rows("provenance_edges"), "claim_evidence_links": links}

    def _restore_evidence_repository(self, repository: Dict[str, Any]) -> None:
        if not repository:
            return
        for source in repository.get("sources", []):
            values = dict(source); metadata = values.pop("metadata", {})
            columns = ["source_id","workspace_id","initiative_id","title","source_type","locator","creator","publisher","published_at","retrieved_at","url","doi","license","access_rights","lifecycle_status","current_version","revision","created_at","updated_at"]
            self.connection.execute(f"INSERT OR REPLACE INTO source_records({','.join(columns)},metadata_json) VALUES ({','.join('?' for _ in range(len(columns)+1))})", [values.get(column) for column in columns] + [canonical_json(metadata)])
        for table, key in (("source_versions", "source_versions"), ("evidence_items", "evidence_items"), ("datasets", "datasets"), ("provenance_edges", "provenance_edges")):
            for item in repository.get(key, []):
                values = dict(item); metadata = values.pop("metadata", {})
                columns = list(values)
                self.connection.execute(f"INSERT OR REPLACE INTO {table}({','.join(columns)},metadata_json) VALUES ({','.join('?' for _ in range(len(columns)+1))})", [values[column] for column in columns] + [canonical_json(metadata)])
        for link in repository.get("claim_evidence_links", []):
            columns = list(link)
            self.connection.execute(f"INSERT OR REPLACE INTO claim_evidence_links({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", [link[column] for column in columns])

    def audit_records(
        self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None, limit: int = 200
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        if workspace_id:
            clauses.append("workspace_id=?")
            params.append(workspace_id)
        if initiative_id:
            clauses.append("initiative_id=?")
            params.append(initiative_id)
        params.append(max(1, min(limit, 1000)))
        rows = self.connection.execute(
            f"SELECT * FROM audit_log WHERE {' AND '.join(clauses)} ORDER BY audit_id DESC LIMIT ?", params
        ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["details"] = json.loads(item.pop("details_json"))
            results.append(item)
        return results

    def export_workspace_bundle(self, workspace_id: str) -> Dict[str, Any]:
        workspace = self.get_entity("workspace", workspace_id, include_archived=True)
        contracts = []
        rows = self.connection.execute(
            "SELECT * FROM canonical_contracts WHERE workspace_id=? ORDER BY initiative_id", (workspace_id,)
        ).fetchall()
        for row in rows:
            item = dict(row)
            item["contract"] = json.loads(item.pop("contract_json"))
            contracts.append(item)
        portfolios = self.list_portfolios(workspace_id, include_archived=True)
        return {
            "bundle_type": "global_impact_workspace_bundle",
            "bundle_version": "2.0.0",
            "database_schema_version": self.schema_version,
            "exported_at": utc_now(),
            "workspace": workspace,
            "contracts": contracts,
            "portfolios": portfolios,
            "evidence_repository": self.export_evidence_repository(workspace_id),
            "indicator_registry": self.export_indicator_registry(workspace_id),
            "measurement_repository": self.export_measurement_repository(workspace_id),
            "review_workflow": self.export_review_workflow(workspace_id),
            "analysis_repository": self.export_analysis_repository(workspace_id),
            "reporting_repository": self.export_reporting_repository(workspace_id),
            "integration_repository": self.export_integration_repository(workspace_id),
            "production_repository": self.export_production_repository(workspace_id),
            "platform_repository": self.export_platform_repository(workspace_id),
            "audit": self.audit_records(workspace_id=workspace_id, limit=1000),
        }

    def restore_workspace_bundle(self, bundle: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        if bundle.get("bundle_type") != "global_impact_workspace_bundle":
            raise UnsupportedImportError("not a Global Impact Catalyst workspace bundle")
        digest = content_hash(bundle)
        existing = self.connection.execute("SELECT * FROM restore_records WHERE bundle_hash=?", (digest,)).fetchone()
        if existing:
            summary = json.loads(existing["summary_json"])
            return {**summary, "status": "unchanged", "restore_id": existing["restore_id"]}
        workspace_id = bundle["workspace"]["entity_id"]
        imported = 0
        unchanged = 0
        for item in bundle.get("contracts", []):
            result = self.record_import(item["contract"], item["contract"], actor=actor, metadata={"restored_from_bundle": digest})
            if result.status == "imported":
                imported += 1
            else:
                unchanged += 1
        for portfolio in bundle.get("portfolios", []):
            try:
                self.get_portfolio(portfolio["portfolio_id"], include_archived=True)
            except NotFoundError:
                self.create_portfolio(portfolio["portfolio_id"], workspace_id, portfolio["name"], portfolio.get("description", ""), actor=actor)
            for initiative_id in portfolio.get("initiative_ids", []):
                self.add_to_portfolio(portfolio["portfolio_id"], initiative_id, actor=actor)
        self._restore_evidence_repository(bundle.get("evidence_repository") or {})
        self._restore_indicator_registry(bundle.get("indicator_registry") or {}, actor=actor)
        self._restore_measurement_repository(bundle.get("measurement_repository") or {}, actor=actor)
        self._restore_review_workflow(bundle.get("review_workflow") or {}, actor=actor)
        self._restore_analysis_repository(bundle.get("analysis_repository") or {}, actor=actor)
        self._restore_reporting_repository(bundle.get("reporting_repository") or {}, actor=actor)
        self._restore_integration_repository(bundle.get("integration_repository") or {}, actor=actor)
        self._restore_production_repository(bundle.get("production_repository") or {}, actor=actor)
        self._restore_platform_repository(bundle.get("platform_repository") or {}, actor=actor)
        restore_id = f"gic-restore-{digest[:20]}"
        summary = {"workspace_id": workspace_id, "contracts_imported": imported, "contracts_unchanged": unchanged}
        self.connection.execute(
            "INSERT INTO restore_records(restore_id, bundle_hash, restored_at, workspace_id, summary_json) VALUES (?, ?, ?, ?, ?)",
            (restore_id, digest, utc_now(), workspace_id, canonical_json(summary)),
        )
        self.connection.commit()
        return {**summary, "status": "restored", "restore_id": restore_id}

    def backup_database(self, destination: str | Path) -> Path:
        if self.database == ":memory:":
            raise RepositoryError("in-memory repositories cannot be copied to a filesystem backup")
        target = Path(destination).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        backup = sqlite3.connect(str(target))
        try:
            self.connection.backup(backup)
        finally:
            backup.close()
        return target

    def repository_summary(self) -> Dict[str, Any]:
        def count(table: str) -> int:
            return int(self.connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
        return {
            "database_schema_version": self.schema_version,
            "workspaces": int(self.connection.execute("SELECT COUNT(*) AS count FROM repository_entities WHERE entity_type='workspace'").fetchone()["count"]),
            "initiatives": int(self.connection.execute("SELECT COUNT(*) AS count FROM repository_entities WHERE entity_type='initiative'").fetchone()["count"]),
            "contracts": count("canonical_contracts"),
            "portfolios": count("portfolios"),
            "imports": count("import_records"),
            "autosaves": count("draft_autosaves"),
            "audit_records": count("audit_log"),
            "sources": count("source_records"),
            "source_versions": count("source_versions"),
            "evidence_items": count("evidence_items"),
            "datasets": count("datasets"),
            "provenance_edges": count("provenance_edges"),
            "claim_evidence_links": count("claim_evidence_links"),
            "units": count("unit_definitions"),
            "indicator_definitions": count("indicator_definitions"),
            "indicator_definition_versions": count("indicator_definition_versions"),
            "baseline_models": count("baseline_models"),
            "target_models": count("target_models"),
            "method_definitions": count("method_definitions"),
            "indicator_registry_bindings": count("indicator_registry_bindings"),
            "impact_results": count("impact_results"),
            "impact_result_relationships": count("impact_result_relationships"),
            "observation_series": count("observation_series"),
            "beneficiary_definitions": count("beneficiary_definitions"),
            "beneficiary_observations": count("beneficiary_observations"),
            "financial_records": count("financial_records"),
            "external_factors": count("external_factors"),
            "contribution_notes": count("contribution_notes"),
            "outcome_portfolios": count("outcome_portfolios"),
            "portfolio_aggregation_runs": count("portfolio_aggregation_runs"),
            "workflow_roles": count("workflow_roles"),
            "review_assignments": count("review_assignments"),
            "review_comments": count("review_comments"),
            "quality_assessments": count("quality_assessments"),
            "approval_decisions": count("approval_decisions"),
            "workflow_revisions": count("workflow_revisions"),
            "correction_records": count("correction_records"),
            "publication_records": count("publication_records"),
            "publication_events": count("publication_events"),
            "analysis_benchmarks": count("analysis_benchmarks"),
            "analysis_comparison_sets": count("analysis_comparison_sets"),
            "analysis_comparison_members": count("analysis_comparison_members"),
            "analysis_scenarios": count("analysis_scenarios"),
            "analysis_uncertainty_models": count("analysis_uncertainty_models"),
            "analysis_runs": count("analysis_runs"),
            "analysis_sensitivity_runs": count("analysis_sensitivity_runs"),
            "report_templates": count("report_templates"),
            "report_documents": count("report_documents"),
            "dashboard_definitions": count("dashboard_definitions"),
            "dashboard_cards": count("dashboard_cards"),
            "publication_snapshots": count("publication_snapshots"),
            "export_bundles": count("export_bundles"),
            "api_clients": count("api_clients"),
            "embeds": count("embed_definitions"),
            "platform_handoffs": count("platform_handoffs"),
            "integration_events": count("integration_events"),
            "export_artifacts": count("export_artifacts"),
            "locales": count("locale_definitions"),
            "offline_packages": count("offline_packages"),
            "offline_changes": count("offline_change_queue"),
            "accessibility_audits": count("accessibility_audits"),
            "security_policies": count("security_policies"),
            "backup_plans": count("backup_plans"),
            "backup_runs": count("backup_runs"),
            "recovery_tests": count("recovery_tests"),
            "deployment_environments": count("deployment_environments"),
            "release_readiness_checks": count("release_readiness_checks"),
            "institutions": count("institutions"),
            "institution_members": count("institution_members"),
            "institution_workspaces": count("institution_workspaces"),
            "platform_connections": count("platform_connections"),
            "decision_pathways": count("decision_pathways"),
            "platform_workflows": count("platform_workflows"),
            "platform_workflow_runs": count("platform_workflow_runs"),
            "platform_snapshots": count("platform_snapshots"),
            "platform_events": count("platform_events"),
        }
