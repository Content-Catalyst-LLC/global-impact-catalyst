"""Persistent repository for Global Impact Catalyst v1.2.0.

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

DATABASE_SCHEMA_VERSION = 3
SUPPORTED_CONTRACT_VERSIONS = {"1.0.0", "1.0.1", "1.1.0", "1.2.0"}
ENTITY_TYPES = {"workspace", "initiative", "goal", "indicator", "observation", "target", "source"}
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
)


class SQLiteImpactRepository:
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
                "SELECT revision, created_at FROM canonical_contracts WHERE record_id=?", (record_id,)
            ).fetchone()
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
            "bundle_version": "1.2.0",
            "database_schema_version": self.schema_version,
            "exported_at": utc_now(),
            "workspace": workspace,
            "contracts": contracts,
            "portfolios": portfolios,
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
        }
