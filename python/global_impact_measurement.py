"""Multi-period observations, beneficiaries, budgets, and outcome portfolios.

Global Impact Catalyst v1.5.0 adds a program-measurement repository around the
canonical v1.1.0 contract and the v1.4.0 indicator registry. The module stores
aggregate records only; individual beneficiary records and direct identifiers
are intentionally outside the core workflow.
"""
from __future__ import annotations

import hashlib
import json
import math
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Sequence

MEASUREMENT_REPOSITORY_VERSION = "1.5.0"
DATA_STATES = {"complete", "missing", "late", "revised", "partial"}
RESULT_TYPES = {"output", "outcome", "long_term_impact"}
RESULT_RELATIONSHIPS = {"contributes_to", "enables", "depends_on", "influences", "is_precondition_for"}
REACH_TYPES = {"direct", "indirect", "combined"}
COUNTING_METHODS = {"unique", "estimated_unique", "encounters", "households", "organizations", "other"}
PRIVACY_LEVELS = {"aggregate_only", "deidentified", "restricted_aggregate"}
OVERLAP_POLICIES = {"no_overlap", "estimated_overlap", "known_overlap", "unknown"}
FINANCIAL_RECORD_TYPES = {"budget", "expenditure", "commitment", "funding"}
CONTRIBUTION_TYPES = {"direct", "indirect", "enabling", "contextual", "unknown"}
EXTERNAL_FACTOR_DIRECTIONS = {"positive", "negative", "mixed", "neutral", "unknown"}
INFLUENCE_LEVELS = {"low", "medium", "high", "unknown"}
PORTFOLIO_AGGREGATIONS = {"sum", "mean", "weighted_mean", "minimum", "maximum"}
PERIOD_POLICIES = {"exact", "same_label", "overlap"}
PORTFOLIO_OVERLAP_POLICIES = {"exclude_unknown_or_overlapping", "allow_with_disclosure", "fail_on_overlap"}
MISSING_DATA_POLICIES = {"exclude_and_disclose", "include_partial", "fail_on_missing"}

# Core workflows accept aggregate dimensions but reject likely direct identifiers.
FORBIDDEN_DIMENSION_KEYS = {
    "name", "full_name", "first_name", "last_name", "email", "email_address",
    "phone", "phone_number", "address", "street_address", "postal_address",
    "ssn", "social_security_number", "date_of_birth", "dob", "passport",
    "driver_license", "person_id", "individual_id", "patient_id",
}


class MeasurementRepositoryError(RuntimeError):
    """Base error for v1.5.0 program measurement operations."""


class PrivacyBoundaryError(MeasurementRepositoryError):
    """Raised when aggregate-only workflows receive direct identifiers."""


class AggregationGuardError(MeasurementRepositoryError):
    """Raised when a portfolio policy requires aggregation to stop."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def measurement_id(kind: str, *parts: Any) -> str:
    material = "|".join(canonical_json(part) if isinstance(part, (dict, list)) else str(part) for part in parts)
    return f"gic-{kind}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


def _finite_or_none(value: Any, field: str) -> Optional[float]:
    if value is None or value == "":
        return None
    number = float(value)
    if not math.isfinite(number):
        raise MeasurementRepositoryError(f"{field} must be finite")
    return number


def _period(record: Dict[str, Any]) -> tuple[Optional[str], Optional[str], str]:
    period = record.get("period") or {}
    start = record.get("period_start", period.get("start"))
    end = record.get("period_end", period.get("end"))
    label = str(record.get("period_label") or period.get("label") or "").strip()
    start = str(start).strip() if start not in (None, "") else None
    end = str(end).strip() if end not in (None, "") else None
    if start and end and start > end:
        raise MeasurementRepositoryError("period_start must not be after period_end")
    if not label:
        label = f"{start or ''}/{end or ''}".strip("/") or "Unspecified period"
    return start, end, label


def _validate_dimensions(dimensions: Any) -> Dict[str, Any]:
    if dimensions in (None, ""):
        return {}
    if not isinstance(dimensions, dict):
        raise MeasurementRepositoryError("dimensions must be an object")
    clean: Dict[str, Any] = {}
    for key, value in dimensions.items():
        normalized = str(key).strip()
        if not normalized:
            raise MeasurementRepositoryError("dimension names cannot be blank")
        if normalized.casefold() in FORBIDDEN_DIMENSION_KEYS:
            raise PrivacyBoundaryError(f"direct identifier dimension is not allowed: {normalized}")
        if isinstance(value, dict):
            raise PrivacyBoundaryError(f"nested person-level dimension is not allowed: {normalized}")
        if isinstance(value, list):
            if any(isinstance(item, (dict, list)) for item in value):
                raise PrivacyBoundaryError(f"nested dimension values are not allowed: {normalized}")
            clean[normalized] = [item for item in value]
        elif value is None or isinstance(value, (str, int, float, bool)):
            clean[normalized] = value
        else:
            raise MeasurementRepositoryError(f"unsupported dimension value for {normalized}")
    return clean


def _period_matches(item: Dict[str, Any], *, start: Optional[str], end: Optional[str], label: str, policy: str) -> bool:
    if policy in {"exact", "same_label"}:
        if label:
            return str(item.get("period_label") or "") == label
        return item.get("period_start") == start and item.get("period_end") == end
    # Overlap is conservative for open-ended periods.
    item_start, item_end = item.get("period_start"), item.get("period_end")
    if not start and not end:
        return True
    if item_start and end and item_start > end:
        return False
    if item_end and start and item_end < start:
        return False
    return True


class MeasurementPortfolioMixin:
    """Mixin implemented by the SQLite reference repository."""

    @contextmanager
    def _measurement_transaction(self) -> Iterator[Any]:
        if self.connection.in_transaction:
            yield self.connection
        else:
            with self.transaction() as connection:
                yield connection

    def _measurement_concurrency(self, entity_type: str, entity_id: str, expected: int, actual: int) -> None:
        raise MeasurementRepositoryError(
            f"stale {entity_type} revision for {entity_id}: expected {expected}, current {actual}"
        )

    @staticmethod
    def _measurement_decode(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            if field in item:
                raw = item.pop(field)
                item[field.removesuffix("_json")] = json.loads(raw or "{}")
        return item

    def register_impact_result(
        self,
        result: Dict[str, Any],
        *,
        workspace_id: str,
        initiative_id: str,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        result_type = str(result.get("result_type") or result.get("type") or "outcome")
        if result_type not in RESULT_TYPES:
            raise MeasurementRepositoryError(f"unsupported impact result type: {result_type}")
        name = str(result.get("name") or result.get("statement") or "").strip()
        if not name:
            raise MeasurementRepositoryError("impact result name is required")
        result_id = str(result.get("result_id") or result.get("id") or measurement_id("result", workspace_id, initiative_id, result_type, name.casefold()))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM impact_results WHERE result_id=?", (result_id,)).fetchone()
        metadata = dict(result.get("metadata") or {})
        lifecycle = str(result.get("lifecycle_status") or result.get("status") or "draft")
        with self._measurement_transaction():
            if existing:
                actual = int(existing["revision"])
                if expected_revision is not None and expected_revision != actual:
                    self._measurement_concurrency("impact_result", result_id, int(expected_revision), actual)
                revision = actual + 1
                self.connection.execute(
                    """UPDATE impact_results SET workspace_id=?,initiative_id=?,result_type=?,name=?,description=?,
                       indicator_definition_id=?,lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE result_id=?""",
                    (workspace_id, initiative_id, result_type, name, str(result.get("description") or result.get("statement") or ""),
                     result.get("indicator_definition_id"), lifecycle, revision, now, canonical_json(metadata), result_id),
                )
                action = "update_impact_result"
            else:
                if expected_revision not in (None, 0):
                    self._measurement_concurrency("impact_result", result_id, int(expected_revision), 0)
                revision = 1
                self.connection.execute(
                    """INSERT INTO impact_results(result_id,workspace_id,initiative_id,result_type,name,description,
                       indicator_definition_id,lifecycle_status,revision,created_at,updated_at,metadata_json)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (result_id, workspace_id, initiative_id, result_type, name,
                     str(result.get("description") or result.get("statement") or ""), result.get("indicator_definition_id"),
                     lifecycle, revision, str(result.get("created_at") or now), now, canonical_json(metadata)),
                )
                action = "create_impact_result"
            self._audit(action, "impact_result", result_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor)
        return self.get_impact_result(result_id)

    def get_impact_result(self, result_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM impact_results WHERE result_id=?", (result_id,)).fetchone()
        if not row:
            raise MeasurementRepositoryError(f"impact result not found: {result_id}")
        return self._measurement_decode(row, "metadata_json")

    def list_impact_results(self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None, result_type: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        if workspace_id: clauses.append("workspace_id=?"); params.append(workspace_id)
        if initiative_id: clauses.append("initiative_id=?"); params.append(initiative_id)
        if result_type: clauses.append("result_type=?"); params.append(result_type)
        rows = self.connection.execute(
            f"SELECT * FROM impact_results WHERE {' AND '.join(clauses)} ORDER BY initiative_id,result_type,name", params
        ).fetchall()
        return [self._measurement_decode(row, "metadata_json") for row in rows]

    def relate_impact_results(
        self,
        from_result_id: str,
        to_result_id: str,
        *,
        relationship_type: str = "contributes_to",
        contribution_weight: Optional[float] = None,
        notes: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        if relationship_type not in RESULT_RELATIONSHIPS:
            raise MeasurementRepositoryError(f"unsupported result relationship: {relationship_type}")
        source, target = self.get_impact_result(from_result_id), self.get_impact_result(to_result_id)
        if source["workspace_id"] != target["workspace_id"] or source["initiative_id"] != target["initiative_id"]:
            raise MeasurementRepositoryError("impact result relationships must remain within one initiative")
        weight = _finite_or_none(contribution_weight, "contribution_weight")
        if weight is not None and not 0 <= weight <= 1:
            raise MeasurementRepositoryError("contribution_weight must be between 0 and 1")
        relationship_id = measurement_id("result-relationship", from_result_id, to_result_id, relationship_type)
        now = utc_now()
        existing = self.connection.execute("SELECT revision,created_at FROM impact_result_relationships WHERE relationship_id=?", (relationship_id,)).fetchone()
        revision = int(existing["revision"]) + 1 if existing else 1
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO impact_result_relationships(relationship_id,workspace_id,initiative_id,from_result_id,to_result_id,
                   relationship_type,contribution_weight,notes,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(relationship_id) DO UPDATE SET contribution_weight=excluded.contribution_weight,
                   notes=excluded.notes,revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (relationship_id, source["workspace_id"], source["initiative_id"], from_result_id, to_result_id,
                 relationship_type, weight, notes, revision, existing["created_at"] if existing else now, now, canonical_json(metadata or {})),
            )
            self._audit("relate_impact_results", "impact_result_relationship", relationship_id, workspace_id=source["workspace_id"], initiative_id=source["initiative_id"], revision=revision, actor=actor)
        row = self.connection.execute("SELECT * FROM impact_result_relationships WHERE relationship_id=?", (relationship_id,)).fetchone()
        return self._measurement_decode(row, "metadata_json")

    def record_observation(
        self,
        observation: Dict[str, Any],
        *,
        workspace_id: str,
        initiative_id: str,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        state = str(observation.get("data_state") or "complete")
        if state not in DATA_STATES:
            raise MeasurementRepositoryError(f"unsupported observation data state: {state}")
        indicator_id = str(observation.get("indicator_id") or "").strip()
        if not indicator_id:
            raise MeasurementRepositoryError("indicator_id is required")
        value = _finite_or_none(observation.get("value"), "observation value")
        if state != "missing" and value is None:
            raise MeasurementRepositoryError("non-missing observations require a value")
        if state == "missing" and value is not None:
            raise MeasurementRepositoryError("missing observations must not contain a value")
        dimensions = _validate_dimensions(observation.get("dimensions") or {})
        denominator = observation.get("denominator") or {}
        if not isinstance(denominator, dict):
            raise MeasurementRepositoryError("denominator must be an object")
        start, end, label = _period(observation)
        unit = self.get_unit(str(observation.get("unit_id") or observation.get("unit") or "count"), workspace_id=workspace_id)
        revision_of = observation.get("revision_of_observation_id")
        if state == "revised" and not revision_of:
            raise MeasurementRepositoryError("revised observations require revision_of_observation_id")
        if revision_of:
            original = self.connection.execute("SELECT * FROM observation_series WHERE observation_record_id=?", (revision_of,)).fetchone()
            if not original:
                raise MeasurementRepositoryError(f"revised observation target not found: {revision_of}")
            if original["initiative_id"] != initiative_id or original["indicator_id"] != indicator_id:
                raise MeasurementRepositoryError("revised observations must reference the same initiative and indicator")
        observation_id = str(observation.get("observation_record_id") or observation.get("id") or measurement_id(
            "observation-record", initiative_id, indicator_id, label, dimensions, revision_of or "base", value
        ))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM observation_series WHERE observation_record_id=?", (observation_id,)).fetchone()
        metadata = dict(observation.get("metadata") or {})
        with self._measurement_transaction():
            if existing:
                actual = int(existing["revision"])
                if expected_revision is not None and expected_revision != actual:
                    self._measurement_concurrency("observation", observation_id, int(expected_revision), actual)
                revision = actual + 1
                created_at = existing["created_at"]
            else:
                if expected_revision not in (None, 0):
                    self._measurement_concurrency("observation", observation_id, int(expected_revision), 0)
                revision = 1
                created_at = str(observation.get("created_at") or now)
            self.connection.execute(
                """INSERT INTO observation_series(observation_record_id,workspace_id,initiative_id,indicator_id,
                   indicator_definition_id,impact_result_id,period_start,period_end,period_label,value,unit_id,data_state,
                   revision_of_observation_id,received_at,revised_at,source_id,method_definition_id,dimensions_json,
                   denominator_json,notes,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(observation_record_id) DO UPDATE SET indicator_definition_id=excluded.indicator_definition_id,
                   impact_result_id=excluded.impact_result_id,period_start=excluded.period_start,period_end=excluded.period_end,
                   period_label=excluded.period_label,value=excluded.value,unit_id=excluded.unit_id,data_state=excluded.data_state,
                   revision_of_observation_id=excluded.revision_of_observation_id,received_at=excluded.received_at,
                   revised_at=excluded.revised_at,source_id=excluded.source_id,method_definition_id=excluded.method_definition_id,
                   dimensions_json=excluded.dimensions_json,denominator_json=excluded.denominator_json,notes=excluded.notes,
                   revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (observation_id, workspace_id, initiative_id, indicator_id, observation.get("indicator_definition_id"),
                 observation.get("impact_result_id"), start, end, label, value, unit["unit_id"], state, revision_of,
                 str(observation.get("received_at") or now), str(observation.get("revised_at") or now) if state == "revised" else observation.get("revised_at"),
                 observation.get("source_id"), observation.get("method_definition_id"), canonical_json(dimensions),
                 canonical_json(denominator), str(observation.get("notes") or ""), revision, created_at, now, canonical_json(metadata)),
            )
            self._audit("record_observation", "observation_record", observation_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor, details={"data_state": state, "period_label": label})
        return self.get_observation(observation_id)

    def get_observation(self, observation_record_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM observation_series WHERE observation_record_id=?", (observation_record_id,)).fetchone()
        if not row:
            raise MeasurementRepositoryError(f"observation not found: {observation_record_id}")
        return self._measurement_decode(row, "dimensions_json", "denominator_json", "metadata_json")

    def list_observations(
        self,
        *,
        workspace_id: Optional[str] = None,
        initiative_id: Optional[str] = None,
        indicator_id: Optional[str] = None,
        indicator_definition_id: Optional[str] = None,
        data_state: Optional[str] = None,
        period_label: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("workspace_id", workspace_id), ("initiative_id", initiative_id), ("indicator_id", indicator_id), ("indicator_definition_id", indicator_definition_id), ("data_state", data_state), ("period_label", period_label)):
            if value is not None:
                clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM observation_series WHERE {' AND '.join(clauses)} ORDER BY COALESCE(period_start,period_label),received_at,observation_record_id", params
        ).fetchall()
        return [self._measurement_decode(row, "dimensions_json", "denominator_json", "metadata_json") for row in rows]

    @staticmethod
    def _effective_records(records: Sequence[Dict[str, Any]], id_field: str, revision_field: str = "revision_of_observation_id") -> List[Dict[str, Any]]:
        superseded = {str(item.get(revision_field)) for item in records if item.get(revision_field)}
        return [item for item in records if str(item.get(id_field)) not in superseded]

    def observation_time_series(self, initiative_id: str, indicator_id: str, *, include_missing: bool = True) -> Dict[str, Any]:
        records = self.list_observations(initiative_id=initiative_id, indicator_id=indicator_id)
        effective = self._effective_records(records, "observation_record_id")
        if not include_missing:
            effective = [item for item in effective if item["data_state"] != "missing"]
        units = sorted({item["unit_id"] for item in effective})
        return {
            "series_type": "global_impact_observation_series",
            "series_version": MEASUREMENT_REPOSITORY_VERSION,
            "initiative_id": initiative_id,
            "indicator_id": indicator_id,
            "generated_at": utc_now(),
            "observations": effective,
            "integrity": {
                "valid": len(units) <= 1,
                "record_count": len(records),
                "effective_record_count": len(effective),
                "unit_ids": units,
                "missing_count": sum(item["data_state"] == "missing" for item in effective),
                "late_count": sum(item["data_state"] == "late" for item in effective),
                "partial_count": sum(item["data_state"] == "partial" for item in effective),
                "revised_count": sum(item["data_state"] == "revised" for item in effective),
            },
        }

    def register_beneficiary_definition(
        self,
        definition: Dict[str, Any],
        *,
        workspace_id: str,
        initiative_id: str,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        name = str(definition.get("name") or "").strip()
        if not name:
            raise MeasurementRepositoryError("beneficiary definition name is required")
        reach = str(definition.get("reach_type") or "direct")
        method = str(definition.get("counting_method") or "unique")
        privacy = str(definition.get("privacy_level") or "aggregate_only")
        overlap = str(definition.get("overlap_policy") or "unknown")
        if reach not in REACH_TYPES: raise MeasurementRepositoryError(f"unsupported reach type: {reach}")
        if method not in COUNTING_METHODS: raise MeasurementRepositoryError(f"unsupported counting method: {method}")
        if privacy not in PRIVACY_LEVELS: raise MeasurementRepositoryError(f"unsupported privacy level: {privacy}")
        if overlap not in OVERLAP_POLICIES: raise MeasurementRepositoryError(f"unsupported overlap policy: {overlap}")
        definition_id = str(definition.get("beneficiary_definition_id") or definition.get("id") or measurement_id("beneficiary-definition", initiative_id, name.casefold(), reach))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM beneficiary_definitions WHERE beneficiary_definition_id=?", (definition_id,)).fetchone()
        revision = int(existing["revision"]) + 1 if existing else 1
        if existing and expected_revision is not None and expected_revision != int(existing["revision"]):
            self._measurement_concurrency("beneficiary_definition", definition_id, int(expected_revision), int(existing["revision"]))
        if not existing and expected_revision not in (None, 0):
            self._measurement_concurrency("beneficiary_definition", definition_id, int(expected_revision), 0)
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO beneficiary_definitions(beneficiary_definition_id,workspace_id,initiative_id,name,description,
                   reach_type,counting_method,privacy_level,overlap_policy,overlap_notes,lifecycle_status,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(beneficiary_definition_id) DO UPDATE SET name=excluded.name,description=excluded.description,
                   reach_type=excluded.reach_type,counting_method=excluded.counting_method,privacy_level=excluded.privacy_level,
                   overlap_policy=excluded.overlap_policy,overlap_notes=excluded.overlap_notes,lifecycle_status=excluded.lifecycle_status,
                   revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (definition_id, workspace_id, initiative_id, name, str(definition.get("description") or ""), reach, method,
                 privacy, overlap, str(definition.get("overlap_notes") or ""), str(definition.get("lifecycle_status") or "draft"),
                 revision, existing["created_at"] if existing else str(definition.get("created_at") or now), now,
                 canonical_json(definition.get("metadata") or {})),
            )
            self._audit("register_beneficiary_definition", "beneficiary_definition", definition_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor)
        return self.get_beneficiary_definition(definition_id)

    def get_beneficiary_definition(self, definition_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM beneficiary_definitions WHERE beneficiary_definition_id=?", (definition_id,)).fetchone()
        if not row:
            raise MeasurementRepositoryError(f"beneficiary definition not found: {definition_id}")
        return self._measurement_decode(row, "metadata_json")

    def list_beneficiary_definitions(self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = ["1=1"]; params: List[Any] = []
        if workspace_id: clauses.append("workspace_id=?"); params.append(workspace_id)
        if initiative_id: clauses.append("initiative_id=?"); params.append(initiative_id)
        rows = self.connection.execute(f"SELECT * FROM beneficiary_definitions WHERE {' AND '.join(clauses)} ORDER BY initiative_id,name", params).fetchall()
        return [self._measurement_decode(row, "metadata_json") for row in rows]

    def record_beneficiary_observation(
        self,
        definition_id: str,
        observation: Dict[str, Any],
        *,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        definition = self.get_beneficiary_definition(definition_id)
        state = str(observation.get("data_state") or "complete")
        if state not in DATA_STATES: raise MeasurementRepositoryError(f"unsupported beneficiary data state: {state}")
        count = _finite_or_none(observation.get("observed_count", observation.get("count")), "beneficiary count")
        if count is not None and count < 0: raise MeasurementRepositoryError("beneficiary counts cannot be negative")
        if state != "missing" and count is None: raise MeasurementRepositoryError("non-missing beneficiary observations require a count")
        if state == "missing" and count is not None: raise MeasurementRepositoryError("missing beneficiary observations must not contain a count")
        dimensions = _validate_dimensions(observation.get("dimensions") or {})
        start, end, label = _period(observation)
        overlap_estimate = _finite_or_none(observation.get("overlap_estimate"), "overlap_estimate")
        if overlap_estimate is not None and (overlap_estimate < 0 or (count is not None and overlap_estimate > count)):
            raise MeasurementRepositoryError("overlap_estimate must be between zero and observed_count")
        revision_of = observation.get("revision_of_observation_id")
        if state == "revised" and not revision_of:
            raise MeasurementRepositoryError("revised beneficiary observations require revision_of_observation_id")
        if revision_of:
            original = self.connection.execute("SELECT * FROM beneficiary_observations WHERE beneficiary_observation_id=?", (revision_of,)).fetchone()
            if not original or original["beneficiary_definition_id"] != definition_id:
                raise MeasurementRepositoryError("beneficiary revision target is missing or incompatible")
        observation_id = str(observation.get("beneficiary_observation_id") or observation.get("id") or measurement_id(
            "beneficiary-observation", definition_id, label, dimensions, revision_of or "base", count
        ))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM beneficiary_observations WHERE beneficiary_observation_id=?", (observation_id,)).fetchone()
        if existing and expected_revision is not None and expected_revision != int(existing["revision"]):
            self._measurement_concurrency("beneficiary_observation", observation_id, int(expected_revision), int(existing["revision"]))
        if not existing and expected_revision not in (None, 0):
            self._measurement_concurrency("beneficiary_observation", observation_id, int(expected_revision), 0)
        revision = int(existing["revision"]) + 1 if existing else 1
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO beneficiary_observations(beneficiary_observation_id,beneficiary_definition_id,workspace_id,
                   initiative_id,period_start,period_end,period_label,observed_count,data_state,revision_of_observation_id,
                   dimensions_json,overlap_estimate,denominator_notes,source_id,received_at,revised_at,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(beneficiary_observation_id) DO UPDATE SET period_start=excluded.period_start,period_end=excluded.period_end,
                   period_label=excluded.period_label,observed_count=excluded.observed_count,data_state=excluded.data_state,
                   revision_of_observation_id=excluded.revision_of_observation_id,dimensions_json=excluded.dimensions_json,
                   overlap_estimate=excluded.overlap_estimate,denominator_notes=excluded.denominator_notes,source_id=excluded.source_id,
                   received_at=excluded.received_at,revised_at=excluded.revised_at,revision=excluded.revision,
                   updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (observation_id, definition_id, definition["workspace_id"], definition["initiative_id"], start, end, label,
                 count, state, revision_of, canonical_json(dimensions), overlap_estimate, str(observation.get("denominator_notes") or ""),
                 observation.get("source_id"), str(observation.get("received_at") or now),
                 str(observation.get("revised_at") or now) if state == "revised" else observation.get("revised_at"), revision,
                 existing["created_at"] if existing else str(observation.get("created_at") or now), now,
                 canonical_json(observation.get("metadata") or {})),
            )
            self._audit("record_beneficiary_observation", "beneficiary_observation", observation_id, workspace_id=definition["workspace_id"], initiative_id=definition["initiative_id"], revision=revision, actor=actor, details={"data_state": state, "period_label": label})
        return self.get_beneficiary_observation(observation_id)

    def get_beneficiary_observation(self, observation_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM beneficiary_observations WHERE beneficiary_observation_id=?", (observation_id,)).fetchone()
        if not row: raise MeasurementRepositoryError(f"beneficiary observation not found: {observation_id}")
        return self._measurement_decode(row, "dimensions_json", "metadata_json")

    def list_beneficiary_observations(self, *, initiative_id: Optional[str] = None, definition_id: Optional[str] = None, period_label: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = ["1=1"]; params: List[Any] = []
        if initiative_id: clauses.append("initiative_id=?"); params.append(initiative_id)
        if definition_id: clauses.append("beneficiary_definition_id=?"); params.append(definition_id)
        if period_label: clauses.append("period_label=?"); params.append(period_label)
        rows = self.connection.execute(f"SELECT * FROM beneficiary_observations WHERE {' AND '.join(clauses)} ORDER BY period_label,received_at", params).fetchall()
        return [self._measurement_decode(row, "dimensions_json", "metadata_json") for row in rows]

    def beneficiary_summary(self, initiative_id: str, *, period_label: Optional[str] = None) -> Dict[str, Any]:
        definitions = {item["beneficiary_definition_id"]: item for item in self.list_beneficiary_definitions(initiative_id=initiative_id)}
        records = self.list_beneficiary_observations(initiative_id=initiative_id, period_label=period_label)
        effective = self._effective_records(records, "beneficiary_observation_id")
        included: List[Dict[str, Any]] = []
        excluded: List[Dict[str, Any]] = []
        direct = indirect = 0.0
        overlap_deduction = 0.0
        assumptions: List[str] = []
        for item in effective:
            definition = definitions.get(item["beneficiary_definition_id"])
            if not definition:
                excluded.append({"beneficiary_observation_id": item["beneficiary_observation_id"], "reason": "definition_missing"}); continue
            if item["data_state"] == "missing" or item["observed_count"] is None:
                excluded.append({"beneficiary_observation_id": item["beneficiary_observation_id"], "reason": "missing_data"}); continue
            count = float(item["observed_count"])
            overlap = float(item.get("overlap_estimate") or 0)
            overlap_deduction += overlap
            if definition["reach_type"] == "direct": direct += count
            elif definition["reach_type"] == "indirect": indirect += count
            else: direct += count
            if definition["overlap_policy"] == "unknown":
                assumptions.append(f"Overlap is unknown for {definition['name']}; totals may contain duplicates.")
            if definition["counting_method"] not in {"unique", "estimated_unique"}:
                assumptions.append(f"{definition['name']} uses {definition['counting_method']} counts rather than confirmed unique people.")
            included.append({**item, "definition": definition})
        gross = direct + indirect
        adjusted = max(0.0, gross - overlap_deduction)
        return {
            "summary_type": "global_impact_beneficiary_summary",
            "summary_version": MEASUREMENT_REPOSITORY_VERSION,
            "initiative_id": initiative_id,
            "period_label": period_label or "all periods",
            "privacy_boundary": "Aggregate records only; no personally identifiable beneficiary data is required.",
            "direct_count": round(direct, 4),
            "indirect_count": round(indirect, 4),
            "gross_count": round(gross, 4),
            "overlap_deduction": round(overlap_deduction, 4),
            "adjusted_count": round(adjusted, 4),
            "included": included,
            "excluded": excluded,
            "assumptions": sorted(set(assumptions)),
        }

    def record_financial_record(
        self,
        record: Dict[str, Any],
        *,
        workspace_id: str,
        initiative_id: str,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        record_type = str(record.get("record_type") or "expenditure")
        if record_type not in FINANCIAL_RECORD_TYPES:
            raise MeasurementRepositoryError(f"unsupported financial record type: {record_type}")
        state = str(record.get("data_state") or "complete")
        if state not in DATA_STATES: raise MeasurementRepositoryError(f"unsupported financial data state: {state}")
        amount = _finite_or_none(record.get("amount"), "financial amount")
        if amount is not None and amount < 0: raise MeasurementRepositoryError("financial amounts cannot be negative")
        if state != "missing" and amount is None: raise MeasurementRepositoryError("non-missing financial records require an amount")
        if state == "missing" and amount is not None: raise MeasurementRepositoryError("missing financial records must not contain an amount")
        currency = str(record.get("currency") or "USD").upper()
        reporting_currency = str(record.get("reporting_currency") or currency).upper()
        exchange_rate = _finite_or_none(record.get("exchange_rate"), "exchange_rate")
        if amount is None:
            reporting_amount = None
        elif currency == reporting_currency:
            exchange_rate = 1.0 if exchange_rate is None else exchange_rate
            reporting_amount = amount * exchange_rate
        else:
            if exchange_rate is None or exchange_rate <= 0:
                raise MeasurementRepositoryError("cross-currency financial records require a positive explicit exchange_rate")
            reporting_amount = amount * exchange_rate
        start, end, label = _period(record)
        record_id = str(record.get("financial_record_id") or record.get("id") or measurement_id(
            "financial-record", initiative_id, record_type, label, currency, record.get("cost_category") or "uncategorized", amount
        ))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM financial_records WHERE financial_record_id=?", (record_id,)).fetchone()
        if existing and expected_revision is not None and expected_revision != int(existing["revision"]):
            self._measurement_concurrency("financial_record", record_id, int(expected_revision), int(existing["revision"]))
        if not existing and expected_revision not in (None, 0):
            self._measurement_concurrency("financial_record", record_id, int(expected_revision), 0)
        revision = int(existing["revision"]) + 1 if existing else 1
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO financial_records(financial_record_id,workspace_id,initiative_id,record_type,funding_source,
                   cost_category,period_start,period_end,period_label,amount,currency,reporting_currency,exchange_rate,
                   reporting_amount,data_state,source_id,notes,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(financial_record_id) DO UPDATE SET record_type=excluded.record_type,funding_source=excluded.funding_source,
                   cost_category=excluded.cost_category,period_start=excluded.period_start,period_end=excluded.period_end,
                   period_label=excluded.period_label,amount=excluded.amount,currency=excluded.currency,
                   reporting_currency=excluded.reporting_currency,exchange_rate=excluded.exchange_rate,
                   reporting_amount=excluded.reporting_amount,data_state=excluded.data_state,source_id=excluded.source_id,
                   notes=excluded.notes,revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (record_id, workspace_id, initiative_id, record_type, str(record.get("funding_source") or ""),
                 str(record.get("cost_category") or "uncategorized"), start, end, label, amount, currency,
                 reporting_currency, exchange_rate, reporting_amount, state, record.get("source_id"), str(record.get("notes") or ""),
                 revision, existing["created_at"] if existing else str(record.get("created_at") or now), now,
                 canonical_json(record.get("metadata") or {})),
            )
            self._audit("record_financial_record", "financial_record", record_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor, details={"record_type": record_type, "period_label": label})
        return self.get_financial_record(record_id)

    def get_financial_record(self, record_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM financial_records WHERE financial_record_id=?", (record_id,)).fetchone()
        if not row: raise MeasurementRepositoryError(f"financial record not found: {record_id}")
        return self._measurement_decode(row, "metadata_json")

    def list_financial_records(self, *, initiative_id: Optional[str] = None, workspace_id: Optional[str] = None, record_type: Optional[str] = None, period_label: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = ["1=1"]; params: List[Any] = []
        for field, value in (("initiative_id", initiative_id), ("workspace_id", workspace_id), ("record_type", record_type), ("period_label", period_label)):
            if value is not None: clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(f"SELECT * FROM financial_records WHERE {' AND '.join(clauses)} ORDER BY period_label,record_type,cost_category", params).fetchall()
        return [self._measurement_decode(row, "metadata_json") for row in rows]

    def financial_summary(self, initiative_id: str, *, period_label: Optional[str] = None, reporting_currency: Optional[str] = None) -> Dict[str, Any]:
        records = self.list_financial_records(initiative_id=initiative_id, period_label=period_label)
        included, excluded = [], []
        totals: Dict[str, float] = {}
        category_totals: Dict[str, float] = {}
        currency = reporting_currency.upper() if reporting_currency else None
        for item in records:
            if item["data_state"] == "missing" or item["reporting_amount"] is None:
                excluded.append({"financial_record_id": item["financial_record_id"], "reason": "missing_data"}); continue
            if currency and item["reporting_currency"] != currency:
                excluded.append({"financial_record_id": item["financial_record_id"], "reason": "reporting_currency_mismatch"}); continue
            if currency is None:
                currency = item["reporting_currency"]
            if item["reporting_currency"] != currency:
                excluded.append({"financial_record_id": item["financial_record_id"], "reason": "mixed_reporting_currency"}); continue
            amount = float(item["reporting_amount"])
            totals[item["record_type"]] = totals.get(item["record_type"], 0.0) + amount
            category_totals[item["cost_category"]] = category_totals.get(item["cost_category"], 0.0) + amount
            included.append(item)
        return {
            "summary_type": "global_impact_financial_summary",
            "summary_version": MEASUREMENT_REPOSITORY_VERSION,
            "initiative_id": initiative_id,
            "period_label": period_label or "all periods",
            "reporting_currency": currency,
            "totals_by_record_type": {key: round(value, 2) for key, value in sorted(totals.items())},
            "totals_by_cost_category": {key: round(value, 2) for key, value in sorted(category_totals.items())},
            "included": included,
            "excluded": excluded,
        }

    def calculate_cost_metric(
        self,
        initiative_id: str,
        *,
        denominator_type: str,
        denominator_id: Optional[str] = None,
        period_label: Optional[str] = None,
        reporting_currency: Optional[str] = None,
        financial_record_types: Sequence[str] = ("expenditure",),
    ) -> Dict[str, Any]:
        financial = self.financial_summary(initiative_id, period_label=period_label, reporting_currency=reporting_currency)
        invalid_types = set(financial_record_types) - FINANCIAL_RECORD_TYPES
        if invalid_types: raise MeasurementRepositoryError(f"unsupported financial record types: {sorted(invalid_types)}")
        numerator = sum(float(financial["totals_by_record_type"].get(kind, 0)) for kind in financial_record_types)
        exclusions: List[Dict[str, Any]] = list(financial["excluded"])
        denominator_value: Optional[float] = None
        denominator_definition = ""
        assumptions: List[str] = []
        if denominator_type == "beneficiary":
            summary = self.beneficiary_summary(initiative_id, period_label=period_label)
            if denominator_id:
                records = [item for item in summary["included"] if item["beneficiary_definition_id"] == denominator_id]
                denominator_value = sum(float(item["observed_count"] or 0) - float(item.get("overlap_estimate") or 0) for item in records)
                definition = self.get_beneficiary_definition(denominator_id)
                denominator_definition = f"{definition['name']} ({definition['counting_method']}, {definition['reach_type']} reach)"
            else:
                denominator_value = float(summary["adjusted_count"])
                denominator_definition = "Adjusted aggregate beneficiary count after recorded overlap deductions"
            assumptions.extend(summary["assumptions"])
            exclusions.extend(summary["excluded"])
        elif denominator_type in {"output", "outcome"}:
            records = self.list_observations(initiative_id=initiative_id, indicator_id=denominator_id) if denominator_id else []
            effective = [item for item in self._effective_records(records, "observation_record_id") if item["data_state"] not in {"missing", "late"}]
            if period_label: effective = [item for item in effective if item["period_label"] == period_label]
            if effective:
                selected = effective[-1]
                denominator_value = float(selected["value"])
                denominator_definition = str((selected.get("denominator") or {}).get("definition") or f"Latest {denominator_type} observation for indicator {selected['indicator_id']}")
                if selected["data_state"] == "partial": assumptions.append("The denominator is a partial-period observation.")
            else:
                exclusions.append({"denominator_id": denominator_id, "reason": "denominator_observation_missing"})
        else:
            raise MeasurementRepositoryError("denominator_type must be beneficiary, output, or outcome")
        value = None if denominator_value in (None, 0) else round(numerator / denominator_value, 4)
        return {
            "metric_type": f"cost_per_{denominator_type}",
            "metric_version": MEASUREMENT_REPOSITORY_VERSION,
            "initiative_id": initiative_id,
            "period_label": period_label or "all periods",
            "numerator": {"value": round(numerator, 2), "currency": financial["reporting_currency"], "record_types": list(financial_record_types)},
            "denominator": {"value": denominator_value, "definition": denominator_definition, "denominator_id": denominator_id},
            "value": value,
            "currency": financial["reporting_currency"],
            "assumptions": assumptions,
            "exclusions": exclusions,
            "boundary": "Cost metrics describe recorded resource use per disclosed denominator; they do not establish efficiency, value for money, or causal impact.",
        }

    def add_external_factor(self, factor: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system") -> Dict[str, Any]:
        name = str(factor.get("name") or "").strip()
        if not name: raise MeasurementRepositoryError("external factor name is required")
        direction = str(factor.get("direction") or "unknown")
        influence = str(factor.get("influence_level") or "unknown")
        if direction not in EXTERNAL_FACTOR_DIRECTIONS: raise MeasurementRepositoryError(f"unsupported factor direction: {direction}")
        if influence not in INFLUENCE_LEVELS: raise MeasurementRepositoryError(f"unsupported influence level: {influence}")
        start, end, label = _period(factor)
        factor_id = str(factor.get("external_factor_id") or factor.get("id") or measurement_id("external-factor", initiative_id, name.casefold(), label))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM external_factors WHERE external_factor_id=?", (factor_id,)).fetchone()
        revision = int(existing["revision"]) + 1 if existing else 1
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO external_factors(external_factor_id,workspace_id,initiative_id,name,description,direction,
                   influence_level,period_start,period_end,period_label,source_id,notes,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(external_factor_id) DO UPDATE SET name=excluded.name,description=excluded.description,
                   direction=excluded.direction,influence_level=excluded.influence_level,period_start=excluded.period_start,
                   period_end=excluded.period_end,period_label=excluded.period_label,source_id=excluded.source_id,
                   notes=excluded.notes,revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (factor_id, workspace_id, initiative_id, name, str(factor.get("description") or ""), direction, influence,
                 start, end, label, factor.get("source_id"), str(factor.get("notes") or ""), revision,
                 existing["created_at"] if existing else str(factor.get("created_at") or now), now,
                 canonical_json(factor.get("metadata") or {})),
            )
            self._audit("add_external_factor", "external_factor", factor_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor)
        return self._measurement_decode(self.connection.execute("SELECT * FROM external_factors WHERE external_factor_id=?", (factor_id,)).fetchone(), "metadata_json")

    def list_external_factors(self, initiative_id: str) -> List[Dict[str, Any]]:
        return [self._measurement_decode(row, "metadata_json") for row in self.connection.execute("SELECT * FROM external_factors WHERE initiative_id=? ORDER BY period_label,name", (initiative_id,)).fetchall()]

    def add_contribution_note(self, note: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system") -> Dict[str, Any]:
        statement = str(note.get("statement") or "").strip()
        if not statement: raise MeasurementRepositoryError("contribution statement is required")
        contribution_type = str(note.get("contribution_type") or "unknown")
        if contribution_type not in CONTRIBUTION_TYPES: raise MeasurementRepositoryError(f"unsupported contribution type: {contribution_type}")
        evidence_refs = [str(item) for item in note.get("evidence_refs") or []]
        factor_refs = [str(item) for item in note.get("external_factor_refs") or []]
        note_id = str(note.get("contribution_note_id") or note.get("id") or measurement_id("contribution-note", initiative_id, note.get("impact_result_id") or "", statement))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM contribution_notes WHERE contribution_note_id=?", (note_id,)).fetchone()
        revision = int(existing["revision"]) + 1 if existing else 1
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO contribution_notes(contribution_note_id,workspace_id,initiative_id,impact_result_id,statement,
                   contribution_type,evidence_refs_json,external_factor_refs_json,limitations,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(contribution_note_id) DO UPDATE SET impact_result_id=excluded.impact_result_id,statement=excluded.statement,
                   contribution_type=excluded.contribution_type,evidence_refs_json=excluded.evidence_refs_json,
                   external_factor_refs_json=excluded.external_factor_refs_json,limitations=excluded.limitations,
                   revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (note_id, workspace_id, initiative_id, note.get("impact_result_id"), statement, contribution_type,
                 canonical_json(evidence_refs), canonical_json(factor_refs), str(note.get("limitations") or ""), revision,
                 existing["created_at"] if existing else str(note.get("created_at") or now), now,
                 canonical_json(note.get("metadata") or {})),
            )
            self._audit("add_contribution_note", "contribution_note", note_id, workspace_id=workspace_id, initiative_id=initiative_id, revision=revision, actor=actor)
        return self._measurement_decode(self.connection.execute("SELECT * FROM contribution_notes WHERE contribution_note_id=?", (note_id,)).fetchone(), "evidence_refs_json", "external_factor_refs_json", "metadata_json")

    def list_contribution_notes(self, initiative_id: str) -> List[Dict[str, Any]]:
        return [self._measurement_decode(row, "evidence_refs_json", "external_factor_refs_json", "metadata_json") for row in self.connection.execute("SELECT * FROM contribution_notes WHERE initiative_id=? ORDER BY created_at", (initiative_id,)).fetchall()]

    def create_outcome_portfolio(
        self,
        portfolio: Dict[str, Any],
        *,
        workspace_id: str,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        name = str(portfolio.get("name") or "").strip()
        if not name: raise MeasurementRepositoryError("outcome portfolio name is required")
        aggregation = str(portfolio.get("aggregation_method") or "sum")
        period_policy = str(portfolio.get("period_policy") or "exact")
        overlap_policy = str(portfolio.get("overlap_policy") or "exclude_unknown_or_overlapping")
        missing_policy = str(portfolio.get("missing_data_policy") or "exclude_and_disclose")
        if aggregation not in PORTFOLIO_AGGREGATIONS: raise MeasurementRepositoryError(f"unsupported portfolio aggregation: {aggregation}")
        if period_policy not in PERIOD_POLICIES: raise MeasurementRepositoryError(f"unsupported period policy: {period_policy}")
        if overlap_policy not in PORTFOLIO_OVERLAP_POLICIES: raise MeasurementRepositoryError(f"unsupported overlap policy: {overlap_policy}")
        if missing_policy not in MISSING_DATA_POLICIES: raise MeasurementRepositoryError(f"unsupported missing-data policy: {missing_policy}")
        target_unit_id = None
        if portfolio.get("target_unit_id") or portfolio.get("target_unit"):
            target_unit_id = self.get_unit(str(portfolio.get("target_unit_id") or portfolio.get("target_unit")), workspace_id=workspace_id)["unit_id"]
        portfolio_id = str(portfolio.get("outcome_portfolio_id") or portfolio.get("id") or measurement_id("outcome-portfolio", workspace_id, name.casefold()))
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM outcome_portfolios WHERE outcome_portfolio_id=?", (portfolio_id,)).fetchone()
        if existing and expected_revision is not None and expected_revision != int(existing["revision"]):
            self._measurement_concurrency("outcome_portfolio", portfolio_id, int(expected_revision), int(existing["revision"]))
        if not existing and expected_revision not in (None, 0):
            self._measurement_concurrency("outcome_portfolio", portfolio_id, int(expected_revision), 0)
        revision = int(existing["revision"]) + 1 if existing else 1
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO outcome_portfolios(outcome_portfolio_id,workspace_id,name,description,aggregation_method,
                   target_unit_id,period_policy,overlap_policy,missing_data_policy,archived_at,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(outcome_portfolio_id) DO UPDATE SET name=excluded.name,description=excluded.description,
                   aggregation_method=excluded.aggregation_method,target_unit_id=excluded.target_unit_id,
                   period_policy=excluded.period_policy,overlap_policy=excluded.overlap_policy,
                   missing_data_policy=excluded.missing_data_policy,revision=excluded.revision,updated_at=excluded.updated_at,
                   metadata_json=excluded.metadata_json""",
                (portfolio_id, workspace_id, name, str(portfolio.get("description") or ""), aggregation, target_unit_id,
                 period_policy, overlap_policy, missing_policy, existing["archived_at"] if existing else None, revision,
                 existing["created_at"] if existing else str(portfolio.get("created_at") or now), now,
                 canonical_json(portfolio.get("metadata") or {})),
            )
            self._audit("create_outcome_portfolio", "outcome_portfolio", portfolio_id, workspace_id=workspace_id, revision=revision, actor=actor)
        return self.get_outcome_portfolio(portfolio_id)

    def add_outcome_portfolio_member(
        self,
        portfolio_id: str,
        member: Dict[str, Any],
        *,
        actor: str = "system",
    ) -> Dict[str, Any]:
        portfolio = self.get_outcome_portfolio(portfolio_id)
        initiative_id = str(member.get("initiative_id") or "").strip()
        indicator_id = str(member.get("indicator_id") or "").strip()
        if not initiative_id or not indicator_id:
            raise MeasurementRepositoryError("outcome portfolio members require initiative_id and indicator_id")
        weight = float(member.get("weight", 1.0))
        if not math.isfinite(weight) or weight <= 0: raise MeasurementRepositoryError("portfolio member weight must be positive")
        membership_id = str(member.get("membership_id") or measurement_id("outcome-membership", portfolio_id, initiative_id, indicator_id, member.get("impact_result_id") or ""))
        with self._measurement_transaction():
            self.connection.execute(
                """INSERT INTO outcome_portfolio_memberships(outcome_portfolio_id,membership_id,initiative_id,indicator_id,
                   indicator_definition_id,impact_result_id,population_scope,overlap_group,denominator_definition,weight,
                   position,added_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(outcome_portfolio_id,membership_id) DO UPDATE SET initiative_id=excluded.initiative_id,
                   indicator_id=excluded.indicator_id,indicator_definition_id=excluded.indicator_definition_id,
                   impact_result_id=excluded.impact_result_id,population_scope=excluded.population_scope,
                   overlap_group=excluded.overlap_group,denominator_definition=excluded.denominator_definition,
                   weight=excluded.weight,position=excluded.position,metadata_json=excluded.metadata_json""",
                (portfolio_id, membership_id, initiative_id, indicator_id, member.get("indicator_definition_id"),
                 member.get("impact_result_id"), str(member.get("population_scope") or ""), str(member.get("overlap_group") or ""),
                 str(member.get("denominator_definition") or ""), weight, int(member.get("position", 0)),
                 str(member.get("added_at") or utc_now()), canonical_json(member.get("metadata") or {})),
            )
            self._audit("add_outcome_portfolio_member", "outcome_portfolio", portfolio_id, workspace_id=portfolio["workspace_id"], initiative_id=initiative_id, revision=portfolio["revision"], actor=actor, details={"membership_id": membership_id})
        return self.get_outcome_portfolio(portfolio_id)

    def get_outcome_portfolio(self, portfolio_id: str, *, include_archived: bool = False) -> Dict[str, Any]:
        query = "SELECT * FROM outcome_portfolios WHERE outcome_portfolio_id=?"
        if not include_archived: query += " AND archived_at IS NULL"
        row = self.connection.execute(query, (portfolio_id,)).fetchone()
        if not row: raise MeasurementRepositoryError(f"outcome portfolio not found: {portfolio_id}")
        portfolio = self._measurement_decode(row, "metadata_json")
        members = self.connection.execute("SELECT * FROM outcome_portfolio_memberships WHERE outcome_portfolio_id=? ORDER BY position,membership_id", (portfolio_id,)).fetchall()
        portfolio["members"] = [self._measurement_decode(item, "metadata_json") for item in members]
        return portfolio

    def list_outcome_portfolios(self, workspace_id: str, *, include_archived: bool = False) -> List[Dict[str, Any]]:
        query = "SELECT outcome_portfolio_id FROM outcome_portfolios WHERE workspace_id=?"
        if not include_archived: query += " AND archived_at IS NULL"
        query += " ORDER BY name"
        return [self.get_outcome_portfolio(row["outcome_portfolio_id"], include_archived=include_archived) for row in self.connection.execute(query, (workspace_id,)).fetchall()]

    def _select_portfolio_observation(self, member: Dict[str, Any], *, start: Optional[str], end: Optional[str], label: str, period_policy: str) -> Optional[Dict[str, Any]]:
        records = self.list_observations(initiative_id=member["initiative_id"], indicator_id=member["indicator_id"])
        effective = self._effective_records(records, "observation_record_id")
        candidates = [item for item in effective if _period_matches(item, start=start, end=end, label=label, policy=period_policy)]
        return candidates[-1] if candidates else None

    def aggregate_outcome_portfolio(
        self,
        portfolio_id: str,
        *,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        period_label: str = "",
        actor: str = "system",
        persist: bool = True,
    ) -> Dict[str, Any]:
        portfolio = self.get_outcome_portfolio(portfolio_id)
        start, end, label = _period({"period_start": period_start, "period_end": period_end, "period_label": period_label})
        included: List[Dict[str, Any]] = []
        excluded: List[Dict[str, Any]] = []
        warnings: List[str] = []
        target_unit = portfolio.get("target_unit_id")
        overlap_groups: set[str] = set()
        observed_labels: set[str] = set()
        for member in portfolio["members"]:
            observation = self._select_portfolio_observation(member, start=start, end=end, label=period_label, period_policy=portfolio["period_policy"])
            if not observation:
                reason = "period_or_observation_missing"
                if portfolio["missing_data_policy"] == "fail_on_missing": raise AggregationGuardError(reason)
                excluded.append({"membership_id": member["membership_id"], "reason": reason}); continue
            observed_labels.add(observation["period_label"])
            if observation["data_state"] in {"missing", "late"} or observation["value"] is None:
                reason = f"data_state_{observation['data_state']}"
                if portfolio["missing_data_policy"] == "fail_on_missing": raise AggregationGuardError(reason)
                excluded.append({"membership_id": member["membership_id"], "observation_record_id": observation["observation_record_id"], "reason": reason}); continue
            if observation["data_state"] == "partial" and portfolio["missing_data_policy"] != "include_partial":
                excluded.append({"membership_id": member["membership_id"], "observation_record_id": observation["observation_record_id"], "reason": "partial_period_excluded"}); continue
            population_sensitive = bool(member.get("denominator_definition") or member.get("population_scope") or (member.get("metadata") or {}).get("population_sensitive"))
            group = str(member.get("overlap_group") or "")
            if portfolio["aggregation_method"] == "sum" and population_sensitive:
                if not group and portfolio["overlap_policy"] == "exclude_unknown_or_overlapping":
                    excluded.append({"membership_id": member["membership_id"], "reason": "population_overlap_unknown"}); continue
                if group and group in overlap_groups:
                    if portfolio["overlap_policy"] == "fail_on_overlap": raise AggregationGuardError(f"overlapping population group: {group}")
                    if portfolio["overlap_policy"] == "exclude_unknown_or_overlapping":
                        excluded.append({"membership_id": member["membership_id"], "reason": "overlapping_population", "overlap_group": group}); continue
                    warnings.append(f"Population overlap group {group} was included and may double count people.")
                if group: overlap_groups.add(group)
            if target_unit is None:
                target_unit = observation["unit_id"]
            try:
                converted = self.convert_value(float(observation["value"]), observation["unit_id"], target_unit, workspace_id=portfolio["workspace_id"])
            except Exception as exc:
                excluded.append({"membership_id": member["membership_id"], "reason": "incompatible_unit", "detail": str(exc), "unit_id": observation["unit_id"]}); continue
            included.append({
                "membership_id": member["membership_id"], "initiative_id": member["initiative_id"],
                "indicator_id": member["indicator_id"], "observation_record_id": observation["observation_record_id"],
                "period_label": observation["period_label"], "source_value": observation["value"],
                "source_unit_id": observation["unit_id"], "converted_value": converted,
                "target_unit_id": target_unit, "weight": float(member["weight"]),
                "population_scope": member.get("population_scope") or "", "overlap_group": group,
                "denominator_definition": member.get("denominator_definition") or "",
                "data_state": observation["data_state"],
            })
        if portfolio["period_policy"] in {"exact", "same_label"} and len(observed_labels) > 1:
            if portfolio["missing_data_policy"] == "fail_on_missing": raise AggregationGuardError("period labels are incompatible")
            keep = sorted(observed_labels)[0]
            for item in list(included):
                if item["period_label"] != keep:
                    included.remove(item); excluded.append({"membership_id": item["membership_id"], "reason": "period_label_mismatch", "period_label": item["period_label"]})
            warnings.append(f"Only period {keep} was retained because member periods differed.")
        values = [float(item["converted_value"]) for item in included]
        method = portfolio["aggregation_method"]
        result_value: Optional[float]
        if not values:
            result_value = None
        elif method == "sum": result_value = sum(values)
        elif method == "mean": result_value = sum(values) / len(values)
        elif method == "weighted_mean":
            weights = [float(item["weight"]) for item in included]
            result_value = sum(value * weight for value, weight in zip(values, weights)) / sum(weights)
        elif method == "minimum": result_value = min(values)
        else: result_value = max(values)
        result_value = round(result_value, 6) if result_value is not None else None
        result = {
            "aggregation_type": "global_impact_outcome_portfolio_aggregation",
            "aggregation_version": MEASUREMENT_REPOSITORY_VERSION,
            "outcome_portfolio_id": portfolio_id,
            "workspace_id": portfolio["workspace_id"],
            "generated_at": utc_now(),
            "period": {"start": start, "end": end, "label": period_label or (next(iter(observed_labels)) if len(observed_labels) == 1 else label)},
            "aggregation_method": method,
            "target_unit_id": target_unit,
            "value": result_value,
            "included": included,
            "excluded": excluded,
            "warnings": sorted(set(warnings)),
            "rules": {
                "period_policy": portfolio["period_policy"],
                "overlap_policy": portfolio["overlap_policy"],
                "missing_data_policy": portfolio["missing_data_policy"],
                "unit_conversion": "Only dimension-compatible units are converted through the governed unit registry.",
                "population_overlap": "Population-sensitive sums disclose or exclude overlapping and unknown scopes according to portfolio policy.",
            },
            "integrity": {"valid": result_value is not None and not any(item["reason"] == "incompatible_unit" for item in excluded), "included_count": len(included), "excluded_count": len(excluded)},
            "boundary": "Portfolio aggregation combines compatible recorded observations; it does not prove attribution or eliminate double-counting risk beyond disclosed rules.",
        }
        if persist:
            run_id = measurement_id("portfolio-run", portfolio_id, result["generated_at"], result["period"], result_value)
            with self._measurement_transaction():
                self.connection.execute(
                    """INSERT INTO portfolio_aggregation_runs(aggregation_run_id,outcome_portfolio_id,workspace_id,
                       period_start,period_end,period_label,aggregation_method,target_unit_id,result_value,result_json,created_at,created_by)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (run_id, portfolio_id, portfolio["workspace_id"], start, end, result["period"]["label"], method, target_unit,
                     result_value, canonical_json(result), result["generated_at"], actor),
                )
                self._audit("aggregate_outcome_portfolio", "outcome_portfolio", portfolio_id, workspace_id=portfolio["workspace_id"], revision=portfolio["revision"], actor=actor, details={"aggregation_run_id": run_id, "included": len(included), "excluded": len(excluded)})
            result["aggregation_run_id"] = run_id
        return result

    def _materialize_contract_measurement(self, contract: Dict[str, Any], *, actor: str = "system") -> None:
        facts = contract["facts"]
        workspace_id = facts["workspace"]["id"]
        initiative_id = facts["initiative"]["id"]
        indicator = facts["indicator"]
        binding = self.connection.execute(
            "SELECT * FROM indicator_registry_bindings WHERE initiative_id=? AND indicator_id=?",
            (initiative_id, indicator["id"]),
        ).fetchone()
        indicator_definition_id = binding["indicator_definition_id"] if binding else None
        method_definition_id = binding["method_definition_id"] if binding else None
        unit_id = binding["unit_id"] if binding else self.get_unit(indicator["definition_version"].get("unit") or "count", workspace_id=workspace_id)["unit_id"]
        outcome_result_ids: List[str] = []
        for outcome in facts.get("outcomes", []):
            result = self.register_impact_result({
                "result_id": outcome["id"], "result_type": "outcome", "name": outcome.get("statement") or "Outcome",
                "description": outcome.get("statement") or "", "indicator_definition_id": indicator_definition_id,
                "lifecycle_status": contract.get("lifecycle_status", "draft"),
                "created_at": outcome.get("created_at"), "metadata": {"record_id": contract["record_id"], "canonical_entity_type": "outcome"},
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)
            outcome_result_ids.append(result["result_id"])
        for observation in facts.get("measurement", {}).get("observations", []):
            source_ids = observation.get("source_ids") or []
            self.record_observation({
                "observation_record_id": observation["id"], "indicator_id": indicator["id"],
                "indicator_definition_id": indicator_definition_id, "impact_result_id": outcome_result_ids[0] if outcome_result_ids else None,
                "period": observation.get("period") or {}, "value": observation.get("value"), "unit_id": unit_id,
                "data_state": "complete", "source_id": source_ids[0] if source_ids else None,
                "method_definition_id": method_definition_id, "received_at": observation.get("updated_at"),
                "created_at": observation.get("created_at"), "metadata": {"record_id": contract["record_id"], "materialized_from_contract": True},
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)
        period = (facts.get("measurement", {}).get("observations") or [{}])[0].get("period") or {}
        for population in facts.get("population_groups", []):
            definition = self.register_beneficiary_definition({
                "beneficiary_definition_id": population["id"], "name": population.get("name") or "Affected population",
                "reach_type": "direct", "counting_method": "estimated_unique", "privacy_level": "aggregate_only",
                "overlap_policy": "unknown", "overlap_notes": "Canonical compact input does not record overlap assumptions.",
                "lifecycle_status": contract.get("lifecycle_status", "draft"),
                "metadata": {"record_id": contract["record_id"], "materialized_from_contract": True},
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)
            count = population.get("observed_count")
            state = "complete" if count is not None else "missing"
            self.record_beneficiary_observation(definition["beneficiary_definition_id"], {
                "beneficiary_observation_id": measurement_id("beneficiary-observation", population["id"], period.get("label") or "current"),
                "period": period, "observed_count": count, "data_state": state,
                "dimensions": {"population_group": population.get("name") or "Affected population"},
                "denominator_notes": "Aggregate count materialized from canonical contract.",
                "received_at": population.get("updated_at"), "created_at": population.get("created_at"),
                "metadata": {"record_id": contract["record_id"], "materialized_from_contract": True},
            }, actor=actor)
        for budget in facts.get("budget_records", []):
            self.record_financial_record({
                "financial_record_id": budget["id"], "record_type": "budget", "period": budget.get("period") or {},
                "amount": budget.get("amount"), "currency": budget.get("currency") or "USD",
                "reporting_currency": budget.get("currency") or "USD", "data_state": "complete" if budget.get("amount") is not None else "missing",
                "created_at": budget.get("created_at"), "metadata": {"record_id": contract["record_id"], "materialized_from_contract": True},
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)

    def export_measurement_repository(self, workspace_id: str) -> Dict[str, Any]:
        def rows(table: str, *, json_fields: Sequence[str] = ("metadata_json",), where: str = "workspace_id=?") -> List[Dict[str, Any]]:
            fetched = self.connection.execute(f"SELECT * FROM {table} WHERE {where} ORDER BY 1", (workspace_id,)).fetchall()
            return [self._measurement_decode(row, *json_fields) for row in fetched]
        results = rows("impact_results")
        relationships = rows("impact_result_relationships")
        observations = rows("observation_series", json_fields=("dimensions_json", "denominator_json", "metadata_json"))
        beneficiaries = rows("beneficiary_definitions")
        beneficiary_observations = rows("beneficiary_observations", json_fields=("dimensions_json", "metadata_json"))
        financial = rows("financial_records")
        factors = rows("external_factors")
        notes = rows("contribution_notes", json_fields=("evidence_refs_json", "external_factor_refs_json", "metadata_json"))
        portfolios = self.list_outcome_portfolios(workspace_id, include_archived=True)
        runs = []
        for row in self.connection.execute("SELECT * FROM portfolio_aggregation_runs WHERE workspace_id=? ORDER BY created_at", (workspace_id,)).fetchall():
            item = dict(row); item["result"] = json.loads(item.pop("result_json")); runs.append(item)
        orphan_relationships = [item["relationship_id"] for item in relationships if not any(result["result_id"] == item["from_result_id"] for result in results) or not any(result["result_id"] == item["to_result_id"] for result in results)]
        direct_identifier_keys: List[str] = []
        for item in [*observations, *beneficiary_observations]:
            direct_identifier_keys.extend(key for key in (item.get("dimensions") or {}) if key.casefold() in FORBIDDEN_DIMENSION_KEYS)
        return {
            "repository_type": "global_impact_measurement_repository",
            "repository_version": MEASUREMENT_REPOSITORY_VERSION,
            "workspace_id": workspace_id,
            "generated_at": utc_now(),
            "impact_results": results,
            "impact_result_relationships": relationships,
            "observations": observations,
            "beneficiary_definitions": beneficiaries,
            "beneficiary_observations": beneficiary_observations,
            "financial_records": financial,
            "external_factors": factors,
            "contribution_notes": notes,
            "outcome_portfolios": portfolios,
            "portfolio_aggregation_runs": runs,
            "integrity": {
                "valid": not orphan_relationships and not direct_identifier_keys,
                "impact_result_count": len(results), "observation_count": len(observations),
                "beneficiary_definition_count": len(beneficiaries), "beneficiary_observation_count": len(beneficiary_observations),
                "financial_record_count": len(financial), "external_factor_count": len(factors),
                "contribution_note_count": len(notes), "outcome_portfolio_count": len(portfolios),
                "aggregation_run_count": len(runs), "orphan_relationship_ids": orphan_relationships,
                "forbidden_dimension_keys": sorted(set(direct_identifier_keys)),
            },
            "privacy_boundary": "The core repository stores aggregate beneficiary counts and dimensions, not individual beneficiary records.",
        }

    def _restore_measurement_repository(self, repository: Dict[str, Any], *, actor: str = "restore") -> None:
        if not repository: return
        workspace_id = repository["workspace_id"]
        for result in repository.get("impact_results", []):
            self.register_impact_result(result, workspace_id=workspace_id, initiative_id=result["initiative_id"], actor=actor)
        for relationship in repository.get("impact_result_relationships", []):
            self.relate_impact_results(relationship["from_result_id"], relationship["to_result_id"], relationship_type=relationship["relationship_type"], contribution_weight=relationship.get("contribution_weight"), notes=relationship.get("notes") or "", metadata=relationship.get("metadata") or {}, actor=actor)
        for item in repository.get("observations", []):
            self.record_observation(item, workspace_id=workspace_id, initiative_id=item["initiative_id"], actor=actor)
        for definition in repository.get("beneficiary_definitions", []):
            self.register_beneficiary_definition(definition, workspace_id=workspace_id, initiative_id=definition["initiative_id"], actor=actor)
        for item in repository.get("beneficiary_observations", []):
            self.record_beneficiary_observation(item["beneficiary_definition_id"], item, actor=actor)
        for item in repository.get("financial_records", []):
            self.record_financial_record(item, workspace_id=workspace_id, initiative_id=item["initiative_id"], actor=actor)
        for item in repository.get("external_factors", []):
            self.add_external_factor(item, workspace_id=workspace_id, initiative_id=item["initiative_id"], actor=actor)
        for item in repository.get("contribution_notes", []):
            self.add_contribution_note(item, workspace_id=workspace_id, initiative_id=item["initiative_id"], actor=actor)
        for portfolio in repository.get("outcome_portfolios", []):
            record = dict(portfolio); members = record.pop("members", [])
            restored = self.create_outcome_portfolio(record, workspace_id=workspace_id, actor=actor)
            for member in members: self.add_outcome_portfolio_member(restored["outcome_portfolio_id"], member, actor=actor)
        # Historical aggregation runs are immutable receipts and can be restored directly.
        for run in repository.get("portfolio_aggregation_runs", []):
            result = run.get("result") or {}
            self.connection.execute(
                """INSERT OR IGNORE INTO portfolio_aggregation_runs(aggregation_run_id,outcome_portfolio_id,workspace_id,
                   period_start,period_end,period_label,aggregation_method,target_unit_id,result_value,result_json,created_at,created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (run["aggregation_run_id"], run["outcome_portfolio_id"], workspace_id, run.get("period_start"), run.get("period_end"),
                 run.get("period_label") or "", run["aggregation_method"], run.get("target_unit_id"), run.get("result_value"),
                 canonical_json(result), run["created_at"], run["created_by"]),
            )
        self.connection.commit()
