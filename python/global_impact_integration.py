"""Versioned public API, governed embeds, and Sustainable Catalyst handoffs.

Global Impact Catalyst v1.9.0 exposes approved publication snapshots through a
privacy-minimizing public contract and creates permissioned, checksum-bound
handoff packages for first-party Sustainable Catalyst products. API and embed
integrity demonstrate identity and provenance; they do not constitute assurance,
certification, factual verification, or causal proof.
"""
from __future__ import annotations

import hashlib
import html
import json
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

INTEGRATION_VERSION = "1.9.0"
API_VERSION = "v1"
JSONLD_CONTEXT_VERSION = "1.0"
API_SCOPES = {
    "public:read", "workspace:read", "reports:read", "exports:read",
    "embeds:write", "handoffs:write", "audit:read",
}
EMBED_TYPES = {"initiative_card", "indicator_trend", "methodology_panel", "portfolio_summary", "report_view"}
HANDOFF_DESTINATIONS = {
    "catalyst_data", "catalyst_analytics_r", "site_intelligence", "workbench",
    "research_lab", "knowledge_library", "research_librarian", "decision_studio",
    "platform_core", "advisory",
}
PUBLIC_BOUNDARY = (
    "Public records are approved publication views. They are not ESG assurance, "
    "SDG certification, audit findings, regulatory filings, factual verification, or causal proof."
)


class IntegrationError(RuntimeError):
    pass


class AuthenticationError(IntegrationError):
    pass


class PermissionDeniedError(IntegrationError):
    pass


class RateLimitError(IntegrationError):
    pass


class IdempotencyConflictError(IntegrationError):
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


def _jsonld_context() -> Dict[str, Any]:
    return {
        "@version": 1.1,
        "gic": "https://sustainablecatalyst.com/ns/global-impact-catalyst/",
        "schema": "https://schema.org/",
        "dcterms": "http://purl.org/dc/terms/",
        "prov": "http://www.w3.org/ns/prov#",
        "sdg": "https://metadata.un.org/sdg/",
        "id": "@id",
        "type": "@type",
        "name": "schema:name",
        "description": "schema:description",
        "datePublished": "schema:datePublished",
        "measurementTechnique": "schema:measurementTechnique",
        "variableMeasured": "schema:variableMeasured",
        "isBasedOn": {"@id": "schema:isBasedOn", "@type": "@id"},
        "wasDerivedFrom": {"@id": "prov:wasDerivedFrom", "@type": "@id"},
    }


class PublicAPIIntegrationMixin:
    @contextmanager
    def _integration_transaction(self) -> Iterator[Any]:
        try:
            self.connection.execute("BEGIN IMMEDIATE")
            yield self.connection
        except Exception:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    @staticmethod
    def _decode_integration(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            db_field = field if field.endswith("_json") else f"{field}_json"
            if db_field in item:
                item[field.removesuffix("_json")] = json.loads(item.pop(db_field) or "{}")
        return item

    # ------------------------------------------------------------------
    # API clients, keys, scopes, idempotency, rate controls, and logging
    # ------------------------------------------------------------------
    def register_api_client(
        self, client: Dict[str, Any], *, workspace_id: Optional[str] = None,
        actor: str = "system", issue_key: bool = True,
    ) -> Dict[str, Any]:
        name = str(client.get("name") or "").strip()
        if not name:
            raise IntegrationError("API client requires name")
        client_type = str(client.get("client_type") or "service")
        if client_type not in {"service", "application", "institution", "developer", "embed"}:
            raise IntegrationError(f"unsupported API client type: {client_type}")
        rate = int(client.get("rate_limit_per_minute") or 60)
        if rate < 1 or rate > 10000:
            raise IntegrationError("rate_limit_per_minute must be between 1 and 10000")
        now = _now()
        client_id = str(client.get("client_id") or _id("api-client", workspace_id or "public", name, now))
        with self._integration_transaction():
            self.connection.execute(
                """INSERT INTO api_clients(client_id,workspace_id,name,description,client_type,lifecycle_status,
                   rate_limit_per_minute,revision,created_by,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (client_id, workspace_id, name, str(client.get("description") or ""), client_type,
                 str(client.get("lifecycle_status") or "active"), rate, 1, actor, now, now,
                 _canonical(client.get("metadata") or {})),
            )
            self._audit("create", "api_client", client_id, workspace_id=workspace_id, actor=actor,
                        details={"client_type": client_type, "rate_limit_per_minute": rate})
        result = self.get_api_client(client_id)
        if issue_key:
            issued = self.issue_api_key(
                client_id, scopes=client.get("scopes") or (["public:read"] if workspace_id is None else ["workspace:read"]),
                expires_at=client.get("expires_at"), actor=actor,
            )
            result["issued_key"] = issued
        return result

    def get_api_client(self, client_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM api_clients WHERE client_id=?", (client_id,)).fetchone()
        if not row:
            raise IntegrationError(f"API client not found: {client_id}")
        item = self._decode_integration(row, "metadata")
        keys = self.connection.execute(
            "SELECT api_key_id,key_prefix,scopes_json,expires_at,revoked_at,last_used_at,created_at FROM api_keys WHERE client_id=? ORDER BY created_at",
            (client_id,),
        ).fetchall()
        item["keys"] = [{**dict(key), "scopes": json.loads(key["scopes_json"])} for key in keys]
        for key in item["keys"]:
            key.pop("scopes_json", None)
        return item

    def issue_api_key(
        self, client_id: str, *, scopes: Sequence[str], expires_at: Optional[str] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        client = self.get_api_client(client_id)
        normalized = sorted({str(scope) for scope in scopes})
        invalid = sorted(set(normalized) - API_SCOPES)
        if invalid:
            raise IntegrationError(f"unsupported API scopes: {', '.join(invalid)}")
        if not normalized:
            raise IntegrationError("at least one API scope is required")
        raw_key = "gic_live_" + secrets.token_urlsafe(32)
        digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        prefix = raw_key[:16]
        now = _now()
        api_key_id = _id("api-key", client_id, digest)
        with self._integration_transaction():
            self.connection.execute(
                """INSERT INTO api_keys(api_key_id,client_id,key_prefix,key_hash,scopes_json,expires_at,revoked_at,
                   last_used_at,created_by,created_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (api_key_id, client_id, prefix, digest, _canonical(normalized), expires_at, None, None, actor, now, "{}"),
            )
            self._audit("issue_key", "api_client", client_id, workspace_id=client.get("workspace_id"), actor=actor,
                        details={"api_key_id": api_key_id, "scopes": normalized, "expires_at": expires_at})
        return {"api_key_id": api_key_id, "client_id": client_id, "api_key": raw_key,
                "key_prefix": prefix, "scopes": normalized, "expires_at": expires_at, "created_at": now}

    def revoke_api_key(self, api_key_id: str, *, actor: str = "system") -> Dict[str, Any]:
        row = self.connection.execute(
            "SELECT k.*,c.workspace_id FROM api_keys k JOIN api_clients c ON c.client_id=k.client_id WHERE api_key_id=?",
            (api_key_id,),
        ).fetchone()
        if not row:
            raise IntegrationError(f"API key not found: {api_key_id}")
        now = _now()
        with self._integration_transaction():
            self.connection.execute("UPDATE api_keys SET revoked_at=? WHERE api_key_id=?", (now, api_key_id))
            self._audit("revoke_key", "api_client", row["client_id"], workspace_id=row["workspace_id"], actor=actor,
                        details={"api_key_id": api_key_id})
        return {"api_key_id": api_key_id, "revoked_at": now}

    def authenticate_api_key(self, api_key: str, *, required_scope: Optional[str] = None) -> Dict[str, Any]:
        digest = hashlib.sha256(str(api_key).encode("utf-8")).hexdigest()
        row = self.connection.execute(
            """SELECT k.*,c.workspace_id,c.name,c.lifecycle_status,c.rate_limit_per_minute
               FROM api_keys k JOIN api_clients c ON c.client_id=k.client_id WHERE k.key_hash=?""", (digest,)
        ).fetchone()
        if not row or row["revoked_at"] or row["lifecycle_status"] != "active":
            raise AuthenticationError("invalid or inactive API key")
        if row["expires_at"]:
            try:
                if datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) <= datetime.now(timezone.utc):
                    raise AuthenticationError("API key has expired")
            except ValueError as exc:
                raise AuthenticationError("API key expiry is invalid") from exc
        scopes = json.loads(row["scopes_json"])
        if required_scope and required_scope not in scopes:
            raise PermissionDeniedError(f"API key lacks required scope: {required_scope}")
        self._enforce_rate_limit(row["client_id"], int(row["rate_limit_per_minute"]))
        self.connection.execute("UPDATE api_keys SET last_used_at=? WHERE api_key_id=?", (_now(), row["api_key_id"]))
        self.connection.commit()
        return {"client_id": row["client_id"], "api_key_id": row["api_key_id"],
                "workspace_id": row["workspace_id"], "client_name": row["name"], "scopes": scopes}

    def _enforce_rate_limit(self, client_id: str, limit: int) -> None:
        now = datetime.now(timezone.utc)
        window = now.replace(second=0, microsecond=0).isoformat()
        with self._integration_transaction():
            row = self.connection.execute(
                "SELECT request_count FROM api_rate_windows WHERE client_id=? AND window_start=?", (client_id, window)
            ).fetchone()
            count = int(row["request_count"]) if row else 0
            if count >= limit:
                raise RateLimitError(f"API rate limit exceeded: {limit} requests per minute")
            self.connection.execute(
                """INSERT INTO api_rate_windows(client_id,window_start,request_count,updated_at) VALUES (?,?,1,?)
                   ON CONFLICT(client_id,window_start) DO UPDATE SET request_count=request_count+1,updated_at=excluded.updated_at""",
                (client_id, window, now.isoformat()),
            )

    def idempotent_operation(
        self, *, client_id: str, idempotency_key: str, operation: str,
        request_payload: Dict[str, Any], execute: Any,
    ) -> Tuple[Dict[str, Any], bool]:
        if not idempotency_key.strip():
            raise IntegrationError("idempotency key is required")
        request_hash = _hash(request_payload)
        existing = self.connection.execute(
            "SELECT * FROM api_idempotency_records WHERE client_id=? AND idempotency_key=? AND operation=?",
            (client_id, idempotency_key, operation),
        ).fetchone()
        if existing:
            if existing["request_hash"] != request_hash:
                raise IdempotencyConflictError("idempotency key was already used with different input")
            return json.loads(existing["response_json"]), True
        response = execute()
        response_hash = _hash(response)
        now = _now()
        expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        with self._integration_transaction():
            self.connection.execute(
                """INSERT INTO api_idempotency_records(idempotency_id,client_id,idempotency_key,operation,
                   request_hash,response_hash,response_json,created_at,expires_at) VALUES (?,?,?,?,?,?,?,?,?)""",
                (_id("idempotency", client_id, operation, idempotency_key), client_id, idempotency_key,
                 operation, request_hash, response_hash, _canonical(response), now, expires),
            )
        return response, False

    def _log_api_access(
        self, *, operation: str, status_code: int, auth: Optional[Dict[str, Any]] = None,
        resource_type: str = "", resource_id: str = "", scope: str = "",
        request_payload: Optional[Dict[str, Any]] = None, response_payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = _now()
        client_id = auth.get("client_id") if auth else None
        key_id = auth.get("api_key_id") if auth else None
        workspace_id = auth.get("workspace_id") if auth else None
        self.connection.execute(
            """INSERT INTO api_access_log(access_id,client_id,api_key_id,workspace_id,operation,resource_type,
               resource_id,scope,status_code,occurred_at,request_hash,response_hash,metadata_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (_id("api-access", operation, resource_id, now, client_id or "public"), client_id, key_id, workspace_id,
             operation, resource_type, resource_id, scope, int(status_code), now,
             _hash(request_payload) if request_payload is not None else "",
             _hash(response_payload) if response_payload is not None else "", _canonical(metadata or {})),
        )
        self.connection.commit()

    # ------------------------------------------------------------------
    # Versioned API envelopes and privacy-safe public resources
    # ------------------------------------------------------------------
    @staticmethod
    def api_envelope(
        data: Any, *, resource_type: str, page: Optional[int] = None,
        page_size: Optional[int] = None, total: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        meta: Dict[str, Any] = {"api_version": API_VERSION, "generated_at": _now(), "resource_type": resource_type}
        if page is not None:
            meta["pagination"] = {"page": page, "page_size": page_size, "total": total,
                                  "page_count": ((total or 0) + (page_size or 1) - 1) // (page_size or 1)}
        if filters:
            meta["filters"] = filters
        return {"@context": _jsonld_context(), "api_version": API_VERSION, "data": data,
                "meta": meta, "boundary": PUBLIC_BOUNDARY}

    @staticmethod
    def api_error(code: str, message: str, *, status: int = 400, field_path: str = "",
                  remediation: str = "") -> Dict[str, Any]:
        return {"api_version": API_VERSION, "error": {"code": code, "message": message,
                "status": status, "field_path": field_path, "remediation": remediation}}

    def _latest_publication_snapshot(self, publication_id: str) -> Dict[str, Any]:
        row = self.connection.execute(
            "SELECT snapshot_id FROM publication_snapshots WHERE publication_id=? ORDER BY created_at DESC,snapshot_id DESC LIMIT 1",
            (publication_id,),
        ).fetchone()
        if not row:
            raise PermissionDeniedError("published record has no approved publication snapshot")
        return self.get_publication_snapshot(row["snapshot_id"])

    def _safe_contract_profile(self, initiative_id: str, expected_hash: str) -> Dict[str, Any]:
        stored = self.get_contract(initiative_id=initiative_id)
        if _hash(stored) != expected_hash:
            raise PermissionDeniedError("current contract no longer matches the approved publication snapshot")
        contract = stored["contract"]
        facts = contract.get("facts") or {}
        measurement = facts.get("measurement") or {}
        observations = measurement.get("observations") or []
        latest = observations[-1] if observations else {}
        return {
            "id": facts.get("initiative", {}).get("id"),
            "name": facts.get("initiative", {}).get("name"),
            "description": facts.get("initiative", {}).get("description", ""),
            "goal": facts.get("goal", {}).get("statement", ""),
            "outcomes": [{"id": item.get("id"), "statement": item.get("statement", "")} for item in facts.get("outcomes") or []],
            "geography": {"name": facts.get("geography", {}).get("name", ""), "type": facts.get("geography", {}).get("geography_type", "")},
            "indicator": {"id": facts.get("indicator", {}).get("id"), "name": facts.get("indicator", {}).get("name"),
                          "definition": facts.get("indicator", {}).get("definition", ""), "direction": facts.get("indicator", {}).get("direction", "")},
            "latest_observation": {"value": latest.get("value"), "unit": latest.get("unit"), "period": latest.get("period")},
            "baseline": measurement.get("baseline"), "target": measurement.get("target"),
            "derived": {"metrics": (contract.get("derived") or {}).get("metrics") or {},
                        "interpretation": (contract.get("derived") or {}).get("interpretation") or {}},
            "contract_version": contract.get("contract_version"),
        }

    def public_catalog(
        self, *, page: int = 1, page_size: int = 20, search: str = "",
        geography: str = "", indicator: str = "",
    ) -> Dict[str, Any]:
        page = max(1, int(page)); page_size = max(1, min(int(page_size), 100))
        clauses = ["p.publication_status='published'", "s.snapshot_id IS NOT NULL"]
        params: List[Any] = []
        if search:
            clauses.append("(LOWER(p.title) LIKE ? OR LOWER(e.name) LIKE ?)")
            term = f"%{search.lower()}%"; params.extend([term, term])
        sql = f"""FROM publication_records p
                  JOIN repository_entities e ON e.entity_type='initiative' AND e.entity_id=p.initiative_id
                  JOIN publication_snapshots s ON s.snapshot_id=(SELECT s2.snapshot_id FROM publication_snapshots s2
                    WHERE s2.publication_id=p.publication_id ORDER BY s2.created_at DESC,s2.snapshot_id DESC LIMIT 1)
                  WHERE {' AND '.join(clauses)}"""
        rows = self.connection.execute(
            f"SELECT p.publication_id,p.initiative_id,p.title,p.release_label,p.public_url,p.published_at,s.snapshot_id,s.snapshot_hash,e.name {sql} ORDER BY p.published_at DESC,p.publication_id LIMIT ? OFFSET ?",
            params + [page_size, (page - 1) * page_size],
        ).fetchall()
        items = []
        for row in rows:
            snapshot = self.get_publication_snapshot(row["snapshot_id"])
            try:
                profile = self._safe_contract_profile(row["initiative_id"], snapshot["contract_hash"])
            except PermissionDeniedError:
                continue
            if geography and geography.lower() not in str(profile.get("geography", {}).get("name", "")).lower():
                continue
            if indicator and indicator.lower() not in str(profile.get("indicator", {}).get("name", "")).lower():
                continue
            items.append({**dict(row), "profile": profile})
        total = int(self.connection.execute(f"SELECT COUNT(*) AS count {sql}", params).fetchone()["count"])
        response = self.api_envelope(items, resource_type="public_initiatives", page=page, page_size=page_size,
                                     total=total, filters={"search": search, "geography": geography, "indicator": indicator})
        self._log_api_access(operation="public_catalog", status_code=200, resource_type="initiative",
                             response_payload=response, metadata={"anonymous": True})
        return response

    def public_publication(self, publication_id: str) -> Dict[str, Any]:
        publication = self.get_publication(publication_id)
        if publication["publication_status"] != "published":
            raise PermissionDeniedError("publication is not public")
        snapshot = self._latest_publication_snapshot(publication_id)
        profile = self._safe_contract_profile(publication["initiative_id"], snapshot["contract_hash"])
        report = snapshot["snapshot"].get("report")
        public_report = None
        if report:
            public_report = {
                "report_id": report.get("report_id"), "title": report.get("title"),
                "report_type": report.get("report_type"), "audience": report.get("audience"),
                "period_label": report.get("period_label"), "content_hash": report.get("content_hash"),
                "document": report.get("document"), "rendered_html": report.get("rendered_html"),
                "rendered_markdown": report.get("rendered_markdown"), "citations": report.get("citations"),
                "methodology": report.get("methodology"),
            }
        data = {
            "publication": {key: publication.get(key) for key in (
                "publication_id", "title", "release_label", "public_url", "published_at", "content_hash")},
            "snapshot": {"snapshot_id": snapshot["snapshot_id"], "snapshot_hash": snapshot["snapshot_hash"],
                         "source_hashes": {key: snapshot[key] for key in (
                             "contract_hash", "evidence_hash", "registry_hash", "measurement_hash",
                             "review_hash", "analysis_hash", "report_hash")}},
            "initiative": profile, "report": public_report,
        }
        response = self.api_envelope(data, resource_type="public_publication")
        self._log_api_access(operation="public_publication", status_code=200, resource_type="publication",
                             resource_id=publication_id, response_payload=response, metadata={"anonymous": True})
        return response

    def workspace_api_resource(
        self, *, api_key: str, workspace_id: str, resource: str,
        page: int = 1, page_size: int = 50,
    ) -> Dict[str, Any]:
        auth = self.authenticate_api_key(api_key, required_scope="workspace:read")
        if auth.get("workspace_id") and auth["workspace_id"] != workspace_id:
            raise PermissionDeniedError("API client is not authorized for this workspace")
        resources = {
            "workspace": lambda: self.get_entity("workspace", workspace_id, include_archived=True),
            "initiatives": lambda: self.list_entities("initiative", workspace_id=workspace_id, include_archived=True),
            "indicators": lambda: self.export_indicator_registry(workspace_id).get("indicator_definitions", []),
            "observations": lambda: self.export_measurement_repository(workspace_id).get("observations", []),
            "sources": lambda: self.list_sources(workspace_id=workspace_id),
            "reviews": lambda: self.export_review_workflow(workspace_id),
            "reports": lambda: self.list_reports(workspace_id=workspace_id),
            "exports": lambda: self.export_reporting_repository(workspace_id).get("export_bundles", []),
        }
        if resource not in resources:
            raise IntegrationError(f"unsupported workspace API resource: {resource}")
        data = resources[resource]()
        if isinstance(data, list):
            page = max(1, int(page)); page_size = max(1, min(int(page_size), 100)); total = len(data)
            data = data[(page - 1) * page_size: page * page_size]
            response = self.api_envelope(data, resource_type=resource, page=page, page_size=page_size, total=total)
        else:
            response = self.api_envelope(data, resource_type=resource)
        self._log_api_access(operation="workspace_resource", status_code=200, auth=auth,
                             resource_type=resource, resource_id=workspace_id, scope="workspace:read",
                             response_payload=response)
        return response

    # ------------------------------------------------------------------
    # Governed public embeds
    # ------------------------------------------------------------------
    def create_embed(
        self, embed: Dict[str, Any], *, workspace_id: str, actor: str = "system",
        expected_revision: Optional[int] = None,
    ) -> Dict[str, Any]:
        embed_type = str(embed.get("embed_type") or "initiative_card")
        if embed_type not in EMBED_TYPES:
            raise IntegrationError(f"unsupported embed type: {embed_type}")
        publication_id = str(embed.get("publication_id") or "")
        publication = self.get_publication(publication_id)
        if publication["publication_status"] != "published" or publication["workspace_id"] != workspace_id:
            raise PermissionDeniedError("embed requires a published record in the selected workspace")
        snapshot = self.get_publication_snapshot(str(embed.get("publication_snapshot_id") or self._latest_publication_snapshot(publication_id)["snapshot_id"]))
        if snapshot["publication_id"] != publication_id:
            raise IntegrationError("publication snapshot does not belong to publication")
        title = str(embed.get("title") or publication["title"]).strip()
        slug = str(embed.get("public_slug") or _id("embed-slug", publication_id, embed_type)[4:]).strip().lower()
        configuration = embed.get("configuration") or {}
        accessibility = embed.get("accessibility") or {"landmark": "region", "heading_level": 2,
                                                          "table_captions": True, "text_alternatives": True}
        content = {"publication_id": publication_id, "snapshot_id": snapshot["snapshot_id"],
                   "snapshot_hash": snapshot["snapshot_hash"], "embed_type": embed_type,
                   "configuration": configuration, "accessibility": accessibility}
        content_hash = _hash(content); now = _now()
        embed_id = str(embed.get("embed_id") or _id("embed", workspace_id, publication_id, embed_type, slug))
        existing = self.connection.execute("SELECT revision,created_at FROM embed_definitions WHERE embed_id=?", (embed_id,)).fetchone()
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and expected_revision != actual:
                self._registry_concurrency("embed", embed_id, expected_revision, actual)
            revision = actual + 1; created_at = existing["created_at"]
        else:
            if expected_revision not in (None, 0):
                self._registry_concurrency("embed", embed_id, expected_revision, 0)
            revision = 1; created_at = now
        with self._integration_transaction():
            self.connection.execute(
                """INSERT OR REPLACE INTO embed_definitions(embed_id,workspace_id,initiative_id,publication_id,
                   publication_snapshot_id,embed_type,title,public_slug,configuration_json,accessibility_json,
                   content_hash,lifecycle_status,revision,created_by,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (embed_id, workspace_id, publication["initiative_id"], publication_id, snapshot["snapshot_id"],
                 embed_type, title, slug, _canonical(configuration), _canonical(accessibility), content_hash,
                 str(embed.get("lifecycle_status") or "active"), revision, actor, created_at, now,
                 _canonical(embed.get("metadata") or {})),
            )
            self._audit("upsert", "embed", embed_id, workspace_id=workspace_id,
                        initiative_id=publication["initiative_id"], revision=revision, actor=actor,
                        details={"embed_type": embed_type, "snapshot_hash": snapshot["snapshot_hash"]})
        return self.get_embed(embed_id)

    def get_embed(self, embed_id_or_slug: str) -> Dict[str, Any]:
        row = self.connection.execute(
            "SELECT * FROM embed_definitions WHERE embed_id=? OR public_slug=?", (embed_id_or_slug, embed_id_or_slug)
        ).fetchone()
        if not row:
            raise IntegrationError(f"embed not found: {embed_id_or_slug}")
        return self._decode_integration(row, "configuration", "accessibility", "metadata")

    def list_embeds(self, workspace_id: str, *, include_inactive: bool = False) -> List[Dict[str, Any]]:
        clauses = ["workspace_id=?"]; params: List[Any] = [workspace_id]
        if not include_inactive:
            clauses.append("lifecycle_status='active'")
        rows = self.connection.execute(
            f"SELECT embed_id FROM embed_definitions WHERE {' AND '.join(clauses)} ORDER BY title,embed_id", params
        ).fetchall()
        return [self.get_embed(row["embed_id"]) for row in rows]

    def render_embed(self, embed_id_or_slug: str) -> Dict[str, Any]:
        embed = self.get_embed(embed_id_or_slug)
        if embed["lifecycle_status"] != "active":
            raise PermissionDeniedError("embed is inactive")
        public = self.public_publication(embed["publication_id"])["data"]
        initiative = public["initiative"]; report = public.get("report") or {}
        title = html.escape(embed["title"]); profile_name = html.escape(str(initiative.get("name") or "Impact initiative"))
        embed_type = embed["embed_type"]
        if embed_type == "report_view" and report:
            body = report.get("rendered_html") or f"<p>{html.escape(str(report.get('title') or 'Report'))}</p>"
        elif embed_type == "methodology_panel":
            methodology = report.get("methodology") or {}
            body = f"<dl><dt>Contract</dt><dd>{html.escape(str(methodology.get('canonical_contract_version') or ''))}</dd><dt>Sources</dt><dd>{int(methodology.get('source_count') or 0)}</dd><dt>Methods</dt><dd>{int(methodology.get('method_count') or 0)}</dd></dl>"
        elif embed_type == "indicator_trend":
            obs = initiative.get("latest_observation") or {}; metrics = (initiative.get("derived") or {}).get("metrics") or {}
            body = f"<p class=\"gic-embed__metric\">{html.escape(str(obs.get('value')))} {html.escape(str(obs.get('unit') or ''))}</p><p>{html.escape(str(obs.get('period') or ''))}</p><p>Progress: {html.escape(str(metrics.get('progress_percent') or metrics.get('progress_to_target_percent') or 'not available'))}</p>"
        elif embed_type == "portfolio_summary":
            body = f"<p>{html.escape(str(initiative.get('goal') or ''))}</p><p>{len(initiative.get('outcomes') or [])} governed outcome record(s).</p>"
        else:
            indicator = initiative.get("indicator") or {}; obs = initiative.get("latest_observation") or {}
            body = f"<p>{html.escape(str(initiative.get('goal') or ''))}</p><dl><dt>Indicator</dt><dd>{html.escape(str(indicator.get('name') or ''))}</dd><dt>Latest observation</dt><dd>{html.escape(str(obs.get('value')))} {html.escape(str(obs.get('unit') or ''))} · {html.escape(str(obs.get('period') or ''))}</dd></dl>"
        markup = (f"<section class=\"gic-public-embed gic-public-embed--{html.escape(embed_type)}\" "
                  f"data-gic-embed=\"{html.escape(embed['embed_id'])}\" aria-labelledby=\"{html.escape(embed['embed_id'])}-title\">"
                  f"<p class=\"gic-public-embed__eyebrow\">Global Impact Catalyst · approved publication</p>"
                  f"<h2 id=\"{html.escape(embed['embed_id'])}-title\">{title}</h2><h3>{profile_name}</h3>{body}"
                  f"<p class=\"gic-public-embed__boundary\">{html.escape(PUBLIC_BOUNDARY)}</p></section>")
        result = {"embed_id": embed["embed_id"], "public_slug": embed["public_slug"], "embed_type": embed_type,
                  "content_hash": embed["content_hash"], "snapshot_hash": public["snapshot"]["snapshot_hash"],
                  "html": markup, "accessibility": embed["accessibility"]}
        self._log_api_access(operation="render_embed", status_code=200, resource_type="embed",
                             resource_id=embed["embed_id"], response_payload=result, metadata={"anonymous": True})
        return result

    # ------------------------------------------------------------------
    # Versioned Sustainable Catalyst handoff packages
    # ------------------------------------------------------------------
    @staticmethod
    def _without_private_evidence(evidence_repository: Dict[str, Any]) -> Dict[str, Any]:
        sources = []
        for source in evidence_repository.get("sources", []):
            sources.append({key: source.get(key) for key in (
                "source_id", "title", "source_type", "creator", "publisher", "published_at", "url", "doi",
                "license", "access_rights", "lifecycle_status", "current_version")})
        return {"repository_version": evidence_repository.get("repository_version"), "sources": sources,
                "datasets": evidence_repository.get("datasets", []), "integrity": evidence_repository.get("integrity", {})}

    def _handoff_source_state(self, workspace_id: str, initiative_id: Optional[str]) -> Dict[str, Any]:
        contracts = []
        if initiative_id:
            contracts = [self.get_contract(initiative_id=initiative_id)]
        else:
            contracts = [self.get_contract(initiative_id=item["entity_id"]) for item in self.list_entities(
                "initiative", workspace_id=workspace_id, include_archived=True)]
        return {
            "workspace": self.get_entity("workspace", workspace_id, include_archived=True),
            "contracts": contracts,
            "evidence": self.export_evidence_repository(workspace_id),
            "registry": self.export_indicator_registry(workspace_id),
            "measurement": self.export_measurement_repository(workspace_id),
            "review": self.export_review_workflow(workspace_id),
            "analysis": self.export_analysis_repository(workspace_id),
            "reporting": self.export_reporting_repository(workspace_id),
        }

    def _handoff_payload(self, destination: str, state: Dict[str, Any], initiative_id: Optional[str]) -> Dict[str, Any]:
        contracts = [item["contract"] for item in state["contracts"]]
        facts = [(item.get("facts") or {}) for item in contracts]
        common = {"workspace": state["workspace"], "initiative_id": initiative_id,
                  "contract_versions": sorted({item.get("contract_version") for item in contracts}),
                  "source_repository_hashes": {key: _hash(value) for key, value in state.items() if key != "workspace"}}
        if destination == "catalyst_data":
            payload = {**common, "datasets": state["evidence"].get("datasets", []),
                       "observations": state["measurement"].get("observations", []),
                       "beneficiary_observations": state["measurement"].get("beneficiary_observations", []),
                       "financial_records": state["measurement"].get("financial_records", []),
                       "data_quality": {"evidence": state["evidence"].get("integrity"), "measurement": state["measurement"].get("integrity")}}
        elif destination == "catalyst_analytics_r":
            payload = {**common, "analysis_repository": state["analysis"],
                       "indicator_definitions": state["registry"].get("indicator_definitions", []),
                       "methods": state["registry"].get("method_definitions", []),
                       "reproducibility": {"formula_language": "gic-expression-1.0", "hash_algorithm": "sha256"}}
        elif destination == "site_intelligence":
            payload = {**common, "geographies": [item.get("geography") for item in facts],
                       "indicators": [item.get("indicator") for item in facts],
                       "observations": state["measurement"].get("observations", []),
                       "publications": [item for item in state["review"].get("publications", []) if item.get("publication_status") == "published"]}
        elif destination in {"workbench", "research_lab"}:
            payload = {**common, "methods": state["registry"].get("method_definitions", []),
                       "baseline_models": state["registry"].get("baseline_models", []),
                       "target_models": state["registry"].get("target_models", []),
                       "scenarios": state["analysis"].get("scenarios", []),
                       "uncertainty_models": state["analysis"].get("uncertainty_models", []),
                       "analysis_runs": state["analysis"].get("analysis_runs", []),
                       "evidence_chain": state["evidence"] if destination == "research_lab" else self._without_private_evidence(state["evidence"])}
        elif destination == "knowledge_library":
            payload = {**common, "evidence_repository": self._without_private_evidence(state["evidence"]),
                       "reports": state["reporting"].get("reports", []),
                       "publication_snapshots": state["reporting"].get("publication_snapshots", []),
                       "citations": [citation for report in state["reporting"].get("reports", []) for citation in report.get("citations", [])]}
        elif destination == "research_librarian":
            payload = {**common, "source_catalog": self._without_private_evidence(state["evidence"]),
                       "research_questions": [item.get("goal", {}).get("statement", "") for item in facts],
                       "topics": [item.get("initiative", {}).get("name", "") for item in facts],
                       "route_hints": ["source discovery", "method review", "comparative evidence", "publication retrieval"]}
        elif destination == "decision_studio":
            payload = {**common, "decision_context": [{"initiative": item.get("initiative"), "goal": item.get("goal"),
                        "outcomes": item.get("outcomes"), "measurement": item.get("measurement")} for item in facts],
                       "analysis": state["analysis"], "quality": state["review"].get("quality_assessments", []),
                       "assumptions": [scenario.get("assumptions", []) for scenario in state["analysis"].get("scenarios", [])],
                       "monitoring_plan": {"observations": state["measurement"].get("observations", []),
                                           "targets": state["registry"].get("target_models", [])}}
        elif destination == "platform_core":
            payload = {**common, "initiative_registry": [item.get("initiative") for item in facts],
                       "publications": state["review"].get("publications", []),
                       "repository_integrity": {key: value.get("integrity", {}) for key, value in state.items() if isinstance(value, dict)},
                       "event_contract": "global-impact-catalyst-event/1.9.0"}
        elif destination == "advisory":
            payload = {**common, "methodology": state["registry"].get("method_definitions", []),
                       "quality_assessments": state["review"].get("quality_assessments", []),
                       "open_corrections": [item for item in state["review"].get("corrections", []) if item.get("status") == "open"],
                       "limitations": [item.get("limitations", []) for item in state["analysis"].get("scenarios", [])],
                       "requested_support": ["methodology review", "measurement design", "implementation planning"]}
        else:
            raise IntegrationError(f"unsupported handoff destination: {destination}")
        return payload

    def create_platform_handoff(
        self, destination: str, *, workspace_id: str, initiative_id: Optional[str] = None,
        idempotency_key: Optional[str] = None, actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if destination not in HANDOFF_DESTINATIONS:
            raise IntegrationError(f"unsupported handoff destination: {destination}")
        if idempotency_key:
            row = self.connection.execute(
                "SELECT handoff_id,payload_hash FROM platform_handoffs WHERE workspace_id=? AND destination=? AND idempotency_key=?",
                (workspace_id, destination, idempotency_key),
            ).fetchone()
            if row:
                return {**self.get_platform_handoff(row["handoff_id"]), "idempotent_replay": True}
        state = self._handoff_source_state(workspace_id, initiative_id)
        source_snapshot_hash = _hash(state)
        payload = {
            "@context": _jsonld_context(),
            "handoff_type": "global_impact_platform_handoff",
            "handoff_version": INTEGRATION_VERSION,
            "destination": destination,
            "created_at": _now(),
            "source_snapshot_hash": source_snapshot_hash,
            "data": self._handoff_payload(destination, state, initiative_id),
            "boundary": "Handoff integrity preserves source identity and governance metadata; receiving systems must retain limitations and may not infer assurance or causal proof.",
        }
        payload_hash = _hash(payload)
        handoff_id = _id("handoff", workspace_id, destination, initiative_id or "workspace", payload_hash)
        now = _now()
        with self._integration_transaction():
            self.connection.execute(
                """INSERT INTO platform_handoffs(handoff_id,workspace_id,initiative_id,destination,handoff_type,
                   handoff_version,status,source_snapshot_hash,payload_hash,payload_json,idempotency_key,created_by,
                   created_at,delivered_at,delivery_receipt_json,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (handoff_id, workspace_id, initiative_id, destination, "global_impact_platform_handoff",
                 INTEGRATION_VERSION, "ready", source_snapshot_hash, payload_hash, _canonical(payload),
                 idempotency_key, actor, now, None, "{}", _canonical(metadata or {})),
            )
            self._audit("create", "platform_handoff", handoff_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, actor=actor,
                        details={"destination": destination, "payload_hash": payload_hash})
            self._emit_integration_event(
                workspace_id=workspace_id, initiative_id=initiative_id, event_type="handoff.ready",
                subject_type="platform_handoff", subject_id=handoff_id,
                payload={"handoff_id": handoff_id, "destination": destination, "payload_hash": payload_hash},
            )
        return self.get_platform_handoff(handoff_id)

    def get_platform_handoff(self, handoff_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM platform_handoffs WHERE handoff_id=?", (handoff_id,)).fetchone()
        if not row:
            raise IntegrationError(f"platform handoff not found: {handoff_id}")
        item = self._decode_integration(row, "payload", "delivery_receipt", "metadata")
        item["integrity"] = {"valid": item["payload_hash"] == _hash(item["payload"]),
                             "actual_payload_hash": _hash(item["payload"])}
        return item

    def list_platform_handoffs(
        self, workspace_id: str, *, destination: Optional[str] = None,
        initiative_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["workspace_id=?"]; params: List[Any] = [workspace_id]
        if destination:
            clauses.append("destination=?"); params.append(destination)
        if initiative_id:
            clauses.append("initiative_id=?"); params.append(initiative_id)
        rows = self.connection.execute(
            f"SELECT handoff_id FROM platform_handoffs WHERE {' AND '.join(clauses)} ORDER BY created_at,handoff_id", params
        ).fetchall()
        return [self.get_platform_handoff(row["handoff_id"]) for row in rows]

    def record_handoff_delivery(
        self, handoff_id: str, receipt: Dict[str, Any], *, actor: str = "system",
    ) -> Dict[str, Any]:
        handoff = self.get_platform_handoff(handoff_id)
        if not handoff["integrity"]["valid"]:
            raise IntegrationError("cannot deliver a handoff with a failed payload hash")
        now = _now()
        with self._integration_transaction():
            self.connection.execute(
                "UPDATE platform_handoffs SET status='delivered',delivered_at=?,delivery_receipt_json=? WHERE handoff_id=?",
                (now, _canonical(receipt), handoff_id),
            )
            self._audit("deliver", "platform_handoff", handoff_id, workspace_id=handoff["workspace_id"],
                        initiative_id=handoff.get("initiative_id"), actor=actor, details={"receipt": receipt})
            self._emit_integration_event(
                workspace_id=handoff["workspace_id"], initiative_id=handoff.get("initiative_id"),
                event_type="handoff.delivered", subject_type="platform_handoff", subject_id=handoff_id,
                payload={"handoff_id": handoff_id, "destination": handoff["destination"], "receipt": receipt},
            )
        return self.get_platform_handoff(handoff_id)

    def _emit_integration_event(
        self, *, workspace_id: Optional[str], initiative_id: Optional[str], event_type: str,
        subject_type: str, subject_id: str, payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        now = _now(); payload_hash = _hash(payload)
        event_id = _id("integration-event", event_type, subject_type, subject_id, payload_hash, now)
        self.connection.execute(
            """INSERT INTO integration_events(event_id,workspace_id,initiative_id,event_type,event_version,
               subject_type,subject_id,payload_hash,payload_json,created_at,metadata_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (event_id, workspace_id, initiative_id, event_type, INTEGRATION_VERSION, subject_type, subject_id,
             payload_hash, _canonical(payload), now, _canonical(metadata or {})),
        )
        return {"event_id": event_id, "event_type": event_type, "event_version": INTEGRATION_VERSION,
                "subject_type": subject_type, "subject_id": subject_id, "payload_hash": payload_hash,
                "payload": payload, "created_at": now}

    # ------------------------------------------------------------------
    # Export, restore, and integrity
    # ------------------------------------------------------------------
    def export_integration_repository(self, workspace_id: str) -> Dict[str, Any]:
        clients = []
        for row in self.connection.execute(
            "SELECT client_id FROM api_clients WHERE workspace_id=? OR workspace_id IS NULL ORDER BY name,client_id", (workspace_id,)
        ):
            client = self.get_api_client(row["client_id"])
            # Never export key hashes, prefixes, or plaintext keys. Non-secret key metadata is enough for audit/rotation.
            client["keys"] = [
                {key: item.get(key) for key in ("api_key_id", "scopes", "expires_at", "revoked_at", "last_used_at", "created_at")}
                for item in client.get("keys", [])
            ]
            clients.append(client)
        embeds = self.list_embeds(workspace_id, include_inactive=True)
        handoffs = self.list_platform_handoffs(workspace_id)
        events = []
        for row in self.connection.execute(
            "SELECT * FROM integration_events WHERE workspace_id=? ORDER BY created_at,event_id", (workspace_id,)
        ):
            events.append(self._decode_integration(row, "payload", "metadata"))
        access_log = []
        for row in self.connection.execute(
            "SELECT * FROM api_access_log WHERE workspace_id=? ORDER BY occurred_at,access_id", (workspace_id,)
        ):
            access_log.append(self._decode_integration(row, "metadata"))
        broken_embeds = []
        for embed in embeds:
            try:
                snapshot = self.get_publication_snapshot(embed["publication_snapshot_id"])
                if embed["content_hash"] != _hash({"publication_id": embed["publication_id"],
                    "snapshot_id": snapshot["snapshot_id"], "snapshot_hash": snapshot["snapshot_hash"],
                    "embed_type": embed["embed_type"], "configuration": embed["configuration"],
                    "accessibility": embed["accessibility"]}):
                    broken_embeds.append(embed["embed_id"])
            except Exception:
                broken_embeds.append(embed["embed_id"])
        broken_handoffs = [item["handoff_id"] for item in handoffs if not item["integrity"]["valid"]]
        broken_events = [item["event_id"] for item in events if item["payload_hash"] != _hash(item["payload"])]
        return {
            "repository_type": "global_impact_integration_repository",
            "repository_version": INTEGRATION_VERSION,
            "api_version": API_VERSION,
            "workspace_id": workspace_id,
            "generated_at": _now(),
            "jsonld_context": _jsonld_context(),
            "api_clients": clients,
            "embeds": embeds,
            "platform_handoffs": handoffs,
            "integration_events": events,
            "api_access_log": access_log,
            "integrity": {"valid": not broken_embeds and not broken_handoffs and not broken_events,
                          "api_client_count": len(clients), "embed_count": len(embeds),
                          "handoff_count": len(handoffs), "event_count": len(events),
                          "access_log_count": len(access_log), "broken_embed_ids": broken_embeds,
                          "broken_handoff_ids": broken_handoffs, "broken_event_ids": broken_events},
            "privacy": {"api_key_material_exported": False, "public_data_requires_published_snapshot": True,
                        "raw_evidence_excerpts_public": False},
            "boundary": PUBLIC_BOUNDARY,
        }

    def _restore_integration_repository(self, repository: Dict[str, Any], *, actor: str = "restore") -> None:
        if not repository:
            return
        workspace_id = repository["workspace_id"]
        for client in repository.get("api_clients", []):
            values = dict(client); values.pop("keys", None); metadata = values.pop("metadata", {})
            columns = ["client_id", "workspace_id", "name", "description", "client_type", "lifecycle_status",
                       "rate_limit_per_minute", "revision", "created_by", "created_at", "updated_at"]
            self.connection.execute(
                f"INSERT OR REPLACE INTO api_clients({','.join(columns)},metadata_json) VALUES ({','.join('?' for _ in range(len(columns)+1))})",
                [values.get(column) for column in columns] + [_canonical(metadata)],
            )
            # Workspace exports intentionally omit plaintext keys, key hashes, and prefixes.
            # Recreate non-authenticating audit tombstones so access-log foreign keys and
            # key rotation history remain lossless without restoring usable credentials.
            for key_record in client.get("keys", []):
                api_key_id = str(key_record.get("api_key_id") or "")
                if not api_key_id:
                    continue
                tombstone_hash = hashlib.sha256(f"restored-audit-tombstone|{api_key_id}".encode("utf-8")).hexdigest()
                self.connection.execute(
                    """INSERT OR REPLACE INTO api_keys(api_key_id,client_id,key_prefix,key_hash,scopes_json,
                       expires_at,revoked_at,last_used_at,created_by,created_at,metadata_json)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (api_key_id, values.get("client_id"), "gic_redacted_", tombstone_hash,
                     _canonical(key_record.get("scopes") or []), key_record.get("expires_at"),
                     key_record.get("revoked_at") or _now(), key_record.get("last_used_at"), actor,
                     key_record.get("created_at") or _now(),
                     _canonical({"restored_without_key_material": True, "authentication_disabled": True})),
                )
        for table, key, json_fields in (
            ("embed_definitions", "embeds", ("configuration", "accessibility", "metadata")),
            ("platform_handoffs", "platform_handoffs", ("payload", "delivery_receipt", "metadata")),
            ("integration_events", "integration_events", ("payload", "metadata")),
            ("api_access_log", "api_access_log", ("metadata",)),
        ):
            for item in repository.get(key, []):
                values = dict(item); values.pop("integrity", None)
                for field in json_fields:
                    values[f"{field}_json"] = _canonical(values.pop(field, {}))
                columns = list(values)
                self.connection.execute(
                    f"INSERT OR REPLACE INTO {table}({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                    [values[column] for column in columns],
                )
        self.connection.commit()
        self._audit("restore", "integration_repository", workspace_id, workspace_id=workspace_id, actor=actor,
                    details={"repository_version": repository.get("repository_version")})
