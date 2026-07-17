"""Indicator, unit, baseline, target, and method registry for v1.4.0.

The registry is deliberately separate from the canonical v1.1.0 impact contract.
It adds reusable governance records and bindings without changing calculation
semantics in previously generated contracts.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional

REGISTRY_VERSION = "1.4.0"
FORMULA_LANGUAGE = "gic-expression-1.0"
INDICATOR_DIRECTIONS = {"higher_is_better", "lower_is_better", "neutral"}
AGGREGATION_METHODS = {"latest", "sum", "mean", "median", "weighted_mean", "rate", "minimum", "maximum"}
BASELINE_METHOD_TYPES = {"point_first", "point_latest", "period_average", "rolling_average", "benchmark", "modelled"}
TARGET_TYPES = {"absolute", "relative_change", "threshold", "range", "trajectory", "formula"}
TRAJECTORY_TYPES = {"linear", "step", "exponential", "custom"}
METHOD_KINDS = {"measurement", "calculation", "sampling", "review", "baseline", "target"}
METHOD_DESIGN_TYPES = {"monitoring", "before_after", "comparison_group", "quasi_experimental", "randomized", "qualitative", "mixed_methods", "administrative", "modelled"}
CONFIDENCE_LEVELS = {"low", "medium", "high", "not_assessed"}
LIFECYCLE_STATUSES = {"draft", "active", "deprecated", "archived"}

ALLOWED_FORMULA_NAMES = {
    "baseline", "current", "target", "period_index", "elapsed_periods",
    "observations_count", "sum_values", "mean_value", "minimum_value", "maximum_value",
}
_ALLOWED_AST_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.UAdd, ast.USub, ast.Load,
)


class IndicatorRegistryError(RuntimeError):
    """Base registry error."""


class FormulaValidationError(IndicatorRegistryError):
    """Raised when a formula is outside the safe expression language."""


class UnitCompatibilityError(IndicatorRegistryError):
    """Raised when units cannot be compared or converted."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def registry_id(kind: str, *parts: Any) -> str:
    material = "|".join(str(part) for part in parts)
    return f"gic-{kind}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


def validate_formula_expression(expression: str, *, allowed_names: Optional[Iterable[str]] = None) -> List[str]:
    """Validate the intentionally small arithmetic expression language."""
    text = str(expression or "").strip()
    if not text:
        return []
    names = set(allowed_names or ALLOWED_FORMULA_NAMES)
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise FormulaValidationError(f"invalid formula syntax: {exc.msg}") from exc
    used: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise FormulaValidationError(f"unsupported formula element: {type(node).__name__}")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise FormulaValidationError("formulas may contain numeric constants only")
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise FormulaValidationError(f"unsupported formula variable: {node.id}")
            used.add(node.id)
    return sorted(used)


def evaluate_formula_expression(expression: str, variables: Dict[str, float]) -> float:
    validate_formula_expression(expression, allowed_names=variables.keys())
    tree = ast.parse(expression, mode="eval")

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            return float(variables[node.id])
        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div):
                if right == 0: raise FormulaValidationError("formula division by zero")
                return left / right
            if isinstance(node.op, ast.Pow): return left ** right
            if isinstance(node.op, ast.Mod):
                if right == 0: raise FormulaValidationError("formula modulo by zero")
                return left % right
        raise FormulaValidationError(f"unsupported formula element: {type(node).__name__}")

    value = evaluate(tree)
    if not math.isfinite(value):
        raise FormulaValidationError("formula result must be finite")
    return float(value)


STANDARD_UNITS: tuple[Dict[str, Any], ...] = (
    {"unit_id": "gic-unit-ratio", "code": "ratio", "symbol": "", "name": "Ratio", "dimension": "dimensionless", "canonical_unit_id": "gic-unit-ratio", "scale_to_canonical": 1.0, "precision_digits": 4},
    {"unit_id": "gic-unit-percent", "code": "%", "symbol": "%", "name": "Percent", "dimension": "dimensionless", "canonical_unit_id": "gic-unit-ratio", "scale_to_canonical": 0.01, "precision_digits": 2},
    {"unit_id": "gic-unit-count", "code": "count", "symbol": "", "name": "Count", "dimension": "count", "canonical_unit_id": "gic-unit-count", "scale_to_canonical": 1.0, "precision_digits": 0},
    {"unit_id": "gic-unit-usd", "code": "USD", "symbol": "$", "name": "US dollar", "dimension": "currency_usd", "canonical_unit_id": "gic-unit-usd", "scale_to_canonical": 1.0, "precision_digits": 2},
    {"unit_id": "gic-unit-kwh", "code": "kWh", "symbol": "kWh", "name": "Kilowatt hour", "dimension": "energy", "canonical_unit_id": "gic-unit-kwh", "scale_to_canonical": 1.0, "precision_digits": 3},
    {"unit_id": "gic-unit-mwh", "code": "MWh", "symbol": "MWh", "name": "Megawatt hour", "dimension": "energy", "canonical_unit_id": "gic-unit-kwh", "scale_to_canonical": 1000.0, "precision_digits": 3},
    {"unit_id": "gic-unit-kg", "code": "kg", "symbol": "kg", "name": "Kilogram", "dimension": "mass", "canonical_unit_id": "gic-unit-kg", "scale_to_canonical": 1.0, "precision_digits": 3},
    {"unit_id": "gic-unit-tonne", "code": "t", "symbol": "t", "name": "Metric tonne", "dimension": "mass", "canonical_unit_id": "gic-unit-kg", "scale_to_canonical": 1000.0, "precision_digits": 3},
    {"unit_id": "gic-unit-kgco2e", "code": "kgCO2e", "symbol": "kgCO₂e", "name": "Kilogram CO2 equivalent", "dimension": "emissions", "canonical_unit_id": "gic-unit-kgco2e", "scale_to_canonical": 1.0, "precision_digits": 3},
    {"unit_id": "gic-unit-tco2e", "code": "tCO2e", "symbol": "tCO₂e", "name": "Metric tonne CO2 equivalent", "dimension": "emissions", "canonical_unit_id": "gic-unit-kgco2e", "scale_to_canonical": 1000.0, "precision_digits": 3},
    {"unit_id": "gic-unit-metre", "code": "m", "symbol": "m", "name": "Metre", "dimension": "length", "canonical_unit_id": "gic-unit-metre", "scale_to_canonical": 1.0, "precision_digits": 3},
    {"unit_id": "gic-unit-kilometre", "code": "km", "symbol": "km", "name": "Kilometre", "dimension": "length", "canonical_unit_id": "gic-unit-metre", "scale_to_canonical": 1000.0, "precision_digits": 3},
    {"unit_id": "gic-unit-square-metre", "code": "m2", "symbol": "m²", "name": "Square metre", "dimension": "area", "canonical_unit_id": "gic-unit-square-metre", "scale_to_canonical": 1.0, "precision_digits": 3},
    {"unit_id": "gic-unit-hectare", "code": "ha", "symbol": "ha", "name": "Hectare", "dimension": "area", "canonical_unit_id": "gic-unit-square-metre", "scale_to_canonical": 10000.0, "precision_digits": 3},
    {"unit_id": "gic-unit-litre", "code": "L", "symbol": "L", "name": "Litre", "dimension": "volume", "canonical_unit_id": "gic-unit-litre", "scale_to_canonical": 1.0, "precision_digits": 3},
    {"unit_id": "gic-unit-cubic-metre", "code": "m3", "symbol": "m³", "name": "Cubic metre", "dimension": "volume", "canonical_unit_id": "gic-unit-litre", "scale_to_canonical": 1000.0, "precision_digits": 3},
    {"unit_id": "gic-unit-hour", "code": "hour", "symbol": "h", "name": "Hour", "dimension": "time", "canonical_unit_id": "gic-unit-hour", "scale_to_canonical": 1.0, "precision_digits": 2},
    {"unit_id": "gic-unit-day", "code": "day", "symbol": "d", "name": "Day", "dimension": "time", "canonical_unit_id": "gic-unit-hour", "scale_to_canonical": 24.0, "precision_digits": 2},
)


class IndicatorRegistryMixin:
    """Mixin implemented by the SQLite repository."""

    @contextmanager
    def _registry_transaction(self) -> Iterator[Any]:
        if self.connection.in_transaction:
            yield self.connection
        else:
            with self.transaction() as connection:
                yield connection

    def _registry_concurrency(self, entity_type: str, entity_id: str, expected: int, actual: int) -> None:
        raise IndicatorRegistryError(
            f"stale {entity_type} revision for {entity_id}: expected {expected}, current {actual}"
        )

    @staticmethod
    def _registry_decode(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            if field in item:
                default = "[]" if field.endswith(("_json",)) and field.split("_")[0] in {"disaggregation", "limitations", "milestones", "input"} else "{}"
                raw = item.pop(field)
                item[field.removesuffix("_json")] = json.loads(raw if raw not in (None, "") else default)
        return item

    def _seed_standard_units(self) -> None:
        now = utc_now()
        with self._registry_transaction():
            for unit in STANDARD_UNITS:
                self.connection.execute(
                    """INSERT OR IGNORE INTO unit_definitions(
                       unit_id,workspace_id,code,symbol,name,dimension,canonical_unit_id,
                       scale_to_canonical,offset_to_canonical,precision_digits,lifecycle_status,
                       revision,created_at,updated_at,metadata_json
                       ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        unit["unit_id"], None, unit["code"], unit.get("symbol", ""), unit["name"],
                        unit["dimension"], unit.get("canonical_unit_id") or unit["unit_id"],
                        float(unit.get("scale_to_canonical", 1.0)), float(unit.get("offset_to_canonical", 0.0)),
                        int(unit.get("precision_digits", 2)), "active", 1, now, now,
                        canonical_json({"standard": True, "registry_version": REGISTRY_VERSION}),
                    ),
                )

    def register_unit(
        self,
        unit: Dict[str, Any],
        *,
        workspace_id: Optional[str] = None,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        code = str(unit.get("code") or "").strip()
        name = str(unit.get("name") or code).strip()
        dimension = str(unit.get("dimension") or "custom").strip().lower()
        if not code or not name:
            raise IndicatorRegistryError("unit code and name are required")
        scale = float(unit.get("scale_to_canonical", 1.0))
        offset = float(unit.get("offset_to_canonical", 0.0))
        precision = int(unit.get("precision_digits", 2))
        if not math.isfinite(scale) or scale == 0 or not math.isfinite(offset):
            raise IndicatorRegistryError("unit conversion scale must be finite and non-zero")
        if precision < 0 or precision > 12:
            raise IndicatorRegistryError("unit precision must be between 0 and 12")
        unit_id = str(unit.get("unit_id") or registry_id("unit", workspace_id or "global", code.casefold()))
        canonical_unit_id = str(unit.get("canonical_unit_id") or unit_id)
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM unit_definitions WHERE unit_id=?", (unit_id,)).fetchone()
        if canonical_unit_id != unit_id:
            canonical = self.connection.execute("SELECT * FROM unit_definitions WHERE unit_id=?", (canonical_unit_id,)).fetchone()
            if not canonical:
                raise IndicatorRegistryError(f"canonical unit not found: {canonical_unit_id}")
            if str(canonical["dimension"]) != dimension:
                raise UnitCompatibilityError("unit and canonical unit dimensions differ")
        metadata = dict(unit.get("metadata") or {})
        lifecycle = str(unit.get("lifecycle_status") or "active")
        if lifecycle not in LIFECYCLE_STATUSES:
            raise IndicatorRegistryError(f"unsupported unit lifecycle status: {lifecycle}")
        with self._registry_transaction():
            if existing:
                actual = int(existing["revision"])
                if expected_revision is not None and expected_revision != actual:
                    self._registry_concurrency("unit", unit_id, int(expected_revision), actual)
                revision = actual + 1
                self.connection.execute(
                    """UPDATE unit_definitions SET workspace_id=?,code=?,symbol=?,name=?,dimension=?,
                       canonical_unit_id=?,scale_to_canonical=?,offset_to_canonical=?,precision_digits=?,
                       lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE unit_id=?""",
                    (workspace_id, code, str(unit.get("symbol") or ""), name, dimension, canonical_unit_id,
                     scale, offset, precision, lifecycle, revision, now, canonical_json(metadata), unit_id),
                )
                action = "update_unit"
            else:
                if expected_revision not in (None, 0):
                    self._registry_concurrency("unit", unit_id, int(expected_revision), 0)
                revision = 1
                self.connection.execute(
                    """INSERT INTO unit_definitions(unit_id,workspace_id,code,symbol,name,dimension,
                       canonical_unit_id,scale_to_canonical,offset_to_canonical,precision_digits,
                       lifecycle_status,revision,created_at,updated_at,metadata_json)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (unit_id, workspace_id, code, str(unit.get("symbol") or ""), name, dimension,
                     canonical_unit_id, scale, offset, precision, lifecycle, revision,
                     str(unit.get("created_at") or now), now, canonical_json(metadata)),
                )
                action = "create_unit"
            self._audit(action, "unit", unit_id, workspace_id=workspace_id, revision=revision, actor=actor)
        return self.get_unit(unit_id)

    def get_unit(self, unit_id_or_code: str, *, workspace_id: Optional[str] = None) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM unit_definitions WHERE unit_id=?", (unit_id_or_code,)).fetchone()
        if not row:
            row = self.connection.execute(
                """SELECT * FROM unit_definitions WHERE LOWER(code)=LOWER(?)
                   AND (workspace_id=? OR workspace_id IS NULL)
                   ORDER BY CASE WHEN workspace_id=? THEN 0 ELSE 1 END LIMIT 1""",
                (unit_id_or_code, workspace_id, workspace_id),
            ).fetchone()
        if not row:
            raise IndicatorRegistryError(f"unit not found: {unit_id_or_code}")
        return self._registry_decode(row, "metadata_json")

    def list_units(self, *, workspace_id: Optional[str] = None, dimension: Optional[str] = None, search: str = "") -> List[Dict[str, Any]]:
        clauses = ["(workspace_id IS NULL" + (" OR workspace_id=?" if workspace_id else "") + ")"]
        params: List[Any] = [workspace_id] if workspace_id else []
        if dimension:
            clauses.append("dimension=?"); params.append(dimension)
        if search:
            clauses.append("(LOWER(code) LIKE ? OR LOWER(name) LIKE ?)")
            like = f"%{search.casefold()}%"; params.extend([like, like])
        rows = self.connection.execute(
            f"SELECT * FROM unit_definitions WHERE {' AND '.join(clauses)} ORDER BY dimension,code", params
        ).fetchall()
        return [self._registry_decode(row, "metadata_json") for row in rows]

    def convert_value(self, value: float, from_unit: str, to_unit: str, *, workspace_id: Optional[str] = None) -> float:
        source = self.get_unit(from_unit, workspace_id=workspace_id)
        target = self.get_unit(to_unit, workspace_id=workspace_id)
        if source["dimension"] != target["dimension"]:
            raise UnitCompatibilityError(
                f"cannot convert {source['code']} ({source['dimension']}) to {target['code']} ({target['dimension']})"
            )
        canonical = float(value) * float(source["scale_to_canonical"]) + float(source["offset_to_canonical"])
        converted = (canonical - float(target["offset_to_canonical"])) / float(target["scale_to_canonical"])
        return round(converted, int(target["precision_digits"]))

    def _versioned_record(
        self,
        *,
        table: str,
        id_field: str,
        entity_id: str,
        version_table: str,
        version_id_field: str,
        hash_field: str,
        json_field: str,
        hash_value: str,
        document: Dict[str, Any],
        version_label: str,
        actor: str,
    ) -> Dict[str, Any]:
        existing = self.connection.execute(
            f"SELECT * FROM {version_table} WHERE {id_field}=? AND {hash_field}=?", (entity_id, hash_value)
        ).fetchone()
        if existing:
            return dict(existing)
        number = int(self.connection.execute(
            f"SELECT COALESCE(MAX(version_number),0)+1 AS number FROM {version_table} WHERE {id_field}=?", (entity_id,)
        ).fetchone()["number"])
        version_id = registry_id(version_id_field.removesuffix("_id"), entity_id, number, hash_value)
        columns = [version_id_field, id_field, "version_number", "version_label", hash_field, json_field, "created_at", "created_by"]
        self.connection.execute(
            f"INSERT INTO {version_table}({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
            (version_id, entity_id, number, version_label or str(number), hash_value, canonical_json(document), utc_now(), actor),
        )
        self.connection.execute(f"UPDATE {table} SET current_version=?,updated_at=? WHERE {id_field}=?", (number, utc_now(), entity_id))
        return dict(self.connection.execute(f"SELECT * FROM {version_table} WHERE {version_id_field}=?", (version_id,)).fetchone())

    def register_indicator_definition(
        self,
        definition: Dict[str, Any],
        *,
        workspace_id: str,
        expected_revision: Optional[int] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        name = str(definition.get("name") or "").strip()
        if not name:
            raise IndicatorRegistryError("indicator definition name is required")
        unit = self.get_unit(str(definition.get("unit_id") or definition.get("unit") or "count"), workspace_id=workspace_id)
        direction = str(definition.get("direction") or "higher_is_better")
        aggregation = str(definition.get("aggregation_method") or "latest")
        formula = str(definition.get("formula_expression") or "").strip()
        if direction not in INDICATOR_DIRECTIONS:
            raise IndicatorRegistryError(f"unsupported indicator direction: {direction}")
        if aggregation not in AGGREGATION_METHODS:
            raise IndicatorRegistryError(f"unsupported aggregation method: {aggregation}")
        formula_variables = validate_formula_expression(formula)
        entity_id = str(definition.get("indicator_definition_id") or definition.get("id") or registry_id("indicator-definition", workspace_id, name.casefold()))
        lifecycle = str(definition.get("lifecycle_status") or "draft")
        if lifecycle not in LIFECYCLE_STATUSES:
            raise IndicatorRegistryError(f"unsupported lifecycle status: {lifecycle}")
        normalized = {
            "indicator_definition_id": entity_id,
            "workspace_id": workspace_id,
            "name": name,
            "description": str(definition.get("description") or ""),
            "direction": direction,
            "unit_id": unit["unit_id"],
            "aggregation_method": aggregation,
            "formula_expression": formula,
            "formula_language": FORMULA_LANGUAGE,
            "formula_variables": formula_variables,
            "disaggregation": list(definition.get("disaggregation") or []),
            "quality_profile": dict(definition.get("quality_profile") or {"status": "not_assessed"}),
            "lifecycle_status": lifecycle,
            "metadata": dict(definition.get("metadata") or {}),
        }
        digest = content_hash(normalized)
        now = utc_now()
        existing = self.connection.execute("SELECT * FROM indicator_definitions WHERE indicator_definition_id=?", (entity_id,)).fetchone()
        with self._registry_transaction():
            if existing:
                actual = int(existing["revision"])
                if expected_revision is not None and expected_revision != actual:
                    self._registry_concurrency("indicator_definition", entity_id, int(expected_revision), actual)
                revision = actual + 1
                self.connection.execute(
                    """UPDATE indicator_definitions SET workspace_id=?,name=?,description=?,direction=?,unit_id=?,
                       aggregation_method=?,formula_expression=?,formula_language=?,disaggregation_json=?,quality_profile_json=?,
                       lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE indicator_definition_id=?""",
                    (workspace_id, name, normalized["description"], direction, unit["unit_id"], aggregation,
                     formula, FORMULA_LANGUAGE, canonical_json(normalized["disaggregation"]), canonical_json(normalized["quality_profile"]),
                     lifecycle, revision, now, canonical_json(normalized["metadata"]), entity_id),
                )
                action = "update_indicator_definition"
            else:
                if expected_revision not in (None, 0):
                    self._registry_concurrency("indicator_definition", entity_id, int(expected_revision), 0)
                revision = 1
                self.connection.execute(
                    """INSERT INTO indicator_definitions(indicator_definition_id,workspace_id,name,description,direction,
                       unit_id,aggregation_method,formula_expression,formula_language,disaggregation_json,quality_profile_json,
                       lifecycle_status,current_version,revision,created_at,updated_at,metadata_json)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (entity_id, workspace_id, name, normalized["description"], direction, unit["unit_id"], aggregation,
                     formula, FORMULA_LANGUAGE, canonical_json(normalized["disaggregation"]), canonical_json(normalized["quality_profile"]),
                     lifecycle, 0, revision, str(definition.get("created_at") or now), now, canonical_json(normalized["metadata"])),
                )
                action = "create_indicator_definition"
            version = self._versioned_record(
                table="indicator_definitions", id_field="indicator_definition_id", entity_id=entity_id,
                version_table="indicator_definition_versions", version_id_field="indicator_definition_version_id",
                hash_field="definition_hash", json_field="definition_json", hash_value=digest,
                document=normalized, version_label=str(definition.get("version_label") or definition.get("version") or ""), actor=actor,
            )
            self._audit(action, "indicator_definition", entity_id, workspace_id=workspace_id, revision=revision, actor=actor,
                        details={"version_id": version["indicator_definition_version_id"], "definition_hash": digest})
        return self.get_indicator_definition(entity_id)

    def get_indicator_definition(self, indicator_definition_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM indicator_definitions WHERE indicator_definition_id=?", (indicator_definition_id,)).fetchone()
        if not row:
            raise IndicatorRegistryError(f"indicator definition not found: {indicator_definition_id}")
        item = self._registry_decode(row, "disaggregation_json", "quality_profile_json", "metadata_json")
        item["versions"] = []
        for version in self.connection.execute(
            "SELECT * FROM indicator_definition_versions WHERE indicator_definition_id=? ORDER BY version_number", (indicator_definition_id,)
        ).fetchall():
            decoded = dict(version); decoded["definition"] = json.loads(decoded.pop("definition_json")); item["versions"].append(decoded)
        return item

    def list_indicator_definitions(self, *, workspace_id: str, search: str = "", include_deprecated: bool = False) -> List[Dict[str, Any]]:
        clauses = ["workspace_id=?"]; params: List[Any] = [workspace_id]
        if search:
            clauses.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ?)"); like=f"%{search.casefold()}%"; params.extend([like,like])
        if not include_deprecated:
            clauses.append("lifecycle_status NOT IN ('deprecated','archived')")
        rows = self.connection.execute(
            f"SELECT indicator_definition_id FROM indicator_definitions WHERE {' AND '.join(clauses)} ORDER BY name", params
        ).fetchall()
        return [self.get_indicator_definition(row["indicator_definition_id"]) for row in rows]

    def register_baseline_model(
        self, model: Dict[str, Any], *, workspace_id: str,
        expected_revision: Optional[int] = None, actor: str = "system",
    ) -> Dict[str, Any]:
        name = str(model.get("name") or "").strip()
        if not name: raise IndicatorRegistryError("baseline model name is required")
        method_type = str(model.get("method_type") or "point_first")
        if method_type not in BASELINE_METHOD_TYPES: raise IndicatorRegistryError(f"unsupported baseline method: {method_type}")
        unit = self.get_unit(str(model.get("unit_id") or model.get("unit") or "count"), workspace_id=workspace_id)
        formula = str(model.get("formula_expression") or "").strip()
        if method_type == "modelled" and not formula: raise IndicatorRegistryError("modelled baselines require a formula")
        variables = validate_formula_expression(formula)
        rolling = model.get("rolling_periods")
        if method_type == "rolling_average" and (rolling is None or int(rolling) < 1):
            raise IndicatorRegistryError("rolling-average baselines require rolling_periods >= 1")
        minimum = int(model.get("minimum_observations", 1))
        if minimum < 1: raise IndicatorRegistryError("minimum_observations must be positive")
        confidence = str(model.get("confidence") or "medium")
        if confidence not in CONFIDENCE_LEVELS: raise IndicatorRegistryError(f"unsupported confidence: {confidence}")
        entity_id = str(model.get("baseline_model_id") or model.get("id") or registry_id("baseline-model", workspace_id, name.casefold()))
        lifecycle = str(model.get("lifecycle_status") or "draft")
        normalized = {
            "baseline_model_id": entity_id, "workspace_id": workspace_id, "name": name,
            "method_type": method_type, "unit_id": unit["unit_id"], "description": str(model.get("description") or ""),
            "period_start": model.get("period_start"), "period_end": model.get("period_end"),
            "rolling_periods": int(rolling) if rolling is not None else None,
            "benchmark_value": float(model["benchmark_value"]) if model.get("benchmark_value") is not None else None,
            "formula_expression": formula, "formula_language": FORMULA_LANGUAGE, "formula_variables": variables,
            "minimum_observations": minimum, "confidence": confidence,
            "parameters": dict(model.get("parameters") or {}), "lifecycle_status": lifecycle,
            "metadata": dict(model.get("metadata") or {}),
        }
        digest = content_hash(normalized); now=utc_now()
        existing=self.connection.execute("SELECT * FROM baseline_models WHERE baseline_model_id=?",(entity_id,)).fetchone()
        with self._registry_transaction():
            if existing:
                actual=int(existing["revision"])
                if expected_revision is not None and expected_revision!=actual: self._registry_concurrency("baseline_model",entity_id,int(expected_revision),actual)
                revision=actual+1
                self.connection.execute("""UPDATE baseline_models SET workspace_id=?,name=?,method_type=?,unit_id=?,description=?,period_start=?,period_end=?,rolling_periods=?,benchmark_value=?,formula_expression=?,formula_language=?,minimum_observations=?,confidence=?,parameters_json=?,lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE baseline_model_id=?""",
                    (workspace_id,name,method_type,unit["unit_id"],normalized["description"],normalized["period_start"],normalized["period_end"],normalized["rolling_periods"],normalized["benchmark_value"],formula,FORMULA_LANGUAGE,minimum,confidence,canonical_json(normalized["parameters"]),lifecycle,revision,now,canonical_json(normalized["metadata"]),entity_id))
                action="update_baseline_model"
            else:
                if expected_revision not in (None,0): self._registry_concurrency("baseline_model",entity_id,int(expected_revision),0)
                revision=1
                self.connection.execute("""INSERT INTO baseline_models(baseline_model_id,workspace_id,name,method_type,unit_id,description,period_start,period_end,rolling_periods,benchmark_value,formula_expression,formula_language,minimum_observations,confidence,parameters_json,lifecycle_status,current_version,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (entity_id,workspace_id,name,method_type,unit["unit_id"],normalized["description"],normalized["period_start"],normalized["period_end"],normalized["rolling_periods"],normalized["benchmark_value"],formula,FORMULA_LANGUAGE,minimum,confidence,canonical_json(normalized["parameters"]),lifecycle,0,revision,str(model.get("created_at") or now),now,canonical_json(normalized["metadata"])))
                action="create_baseline_model"
            version=self._versioned_record(table="baseline_models",id_field="baseline_model_id",entity_id=entity_id,version_table="baseline_model_versions",version_id_field="baseline_model_version_id",hash_field="model_hash",json_field="model_json",hash_value=digest,document=normalized,version_label=str(model.get("version_label") or model.get("version") or ""),actor=actor)
            self._audit(action,"baseline_model",entity_id,workspace_id=workspace_id,revision=revision,actor=actor,details={"version_id":version["baseline_model_version_id"],"model_hash":digest})
        return self.get_baseline_model(entity_id)

    def get_baseline_model(self, baseline_model_id: str) -> Dict[str, Any]:
        row=self.connection.execute("SELECT * FROM baseline_models WHERE baseline_model_id=?",(baseline_model_id,)).fetchone()
        if not row: raise IndicatorRegistryError(f"baseline model not found: {baseline_model_id}")
        item=self._registry_decode(row,"parameters_json","metadata_json"); item["versions"]=[]
        for version in self.connection.execute("SELECT * FROM baseline_model_versions WHERE baseline_model_id=? ORDER BY version_number",(baseline_model_id,)).fetchall():
            decoded=dict(version); decoded["model"]=json.loads(decoded.pop("model_json")); item["versions"].append(decoded)
        return item

    def compute_baseline(self, baseline_model_id: str, observations: Iterable[Any]) -> Dict[str, Any]:
        model=self.get_baseline_model(baseline_model_id)
        values=[float(item.get("value")) if isinstance(item,dict) else float(item) for item in observations]
        if len(values)<int(model["minimum_observations"]):
            raise IndicatorRegistryError("insufficient observations for baseline model")
        method=model["method_type"]
        if method=="point_first": used=values[:1]; value=used[0]
        elif method=="point_latest": used=values[-1:]; value=used[0]
        elif method=="period_average": used=values; value=sum(used)/len(used)
        elif method=="rolling_average": used=values[-int(model["rolling_periods"]):]; value=sum(used)/len(used)
        elif method=="benchmark":
            if model["benchmark_value"] is None: raise IndicatorRegistryError("benchmark baseline has no benchmark value")
            used=[]; value=float(model["benchmark_value"])
        else:
            variables={"baseline":values[0],"current":values[-1],"target":float(model["benchmark_value"] or 0),"period_index":float(len(values)-1),"elapsed_periods":float(max(0,len(values)-1)),"observations_count":float(len(values)),"sum_values":float(sum(values)),"mean_value":float(sum(values)/len(values)),"minimum_value":float(min(values)),"maximum_value":float(max(values))}
            used=values; value=evaluate_formula_expression(model["formula_expression"],variables)
        unit=self.get_unit(model["unit_id"],workspace_id=model["workspace_id"])
        return {"baseline_model_id":baseline_model_id,"baseline_model_version_id":model["versions"][-1]["baseline_model_version_id"],"value":round(float(value),int(unit["precision_digits"])),"unit_id":unit["unit_id"],"method_type":method,"observations_used":len(used)}

    def register_target_model(self, model: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int]=None, actor: str="system") -> Dict[str, Any]:
        name=str(model.get("name") or "").strip()
        if not name: raise IndicatorRegistryError("target model name is required")
        target_type=str(model.get("target_type") or "absolute")
        trajectory=str(model.get("trajectory_type") or "linear")
        direction=str(model.get("direction") or "higher_is_better")
        if target_type not in TARGET_TYPES: raise IndicatorRegistryError(f"unsupported target type: {target_type}")
        if trajectory not in TRAJECTORY_TYPES: raise IndicatorRegistryError(f"unsupported trajectory type: {trajectory}")
        if direction not in INDICATOR_DIRECTIONS: raise IndicatorRegistryError(f"unsupported target direction: {direction}")
        unit=self.get_unit(str(model.get("unit_id") or model.get("unit") or "count"),workspace_id=workspace_id)
        indicator_definition_id=model.get("indicator_definition_id")
        if indicator_definition_id:
            indicator=self.get_indicator_definition(str(indicator_definition_id))
            indicator_unit=self.get_unit(indicator["unit_id"],workspace_id=workspace_id)
            if indicator_unit["dimension"]!=unit["dimension"]: raise UnitCompatibilityError("target and indicator units are incompatible")
        formula=str(model.get("formula_expression") or "").strip(); variables=validate_formula_expression(formula)
        milestones=list(model.get("milestones") or [])
        for index,milestone in enumerate(milestones):
            if "value" not in milestone: raise IndicatorRegistryError(f"target milestone {index} requires value")
            milestone.setdefault("position", index/(max(1,len(milestones)-1)))
        if target_type in {"absolute","threshold"} and model.get("target_value") is None: raise IndicatorRegistryError(f"{target_type} targets require target_value")
        if target_type=="range" and (model.get("lower_value") is None or model.get("upper_value") is None): raise IndicatorRegistryError("range targets require lower_value and upper_value")
        if target_type=="relative_change" and model.get("relative_change_percent") is None: raise IndicatorRegistryError("relative-change targets require relative_change_percent")
        if target_type=="formula" and not formula: raise IndicatorRegistryError("formula targets require formula_expression")
        entity_id=str(model.get("target_model_id") or model.get("id") or registry_id("target-model",workspace_id,name.casefold()))
        lifecycle=str(model.get("lifecycle_status") or "draft")
        number=lambda key: float(model[key]) if model.get(key) is not None else None
        normalized={"target_model_id":entity_id,"workspace_id":workspace_id,"indicator_definition_id":indicator_definition_id,"name":name,"target_type":target_type,"unit_id":unit["unit_id"],"direction":direction,"target_value":number("target_value"),"lower_value":number("lower_value"),"upper_value":number("upper_value"),"relative_change_percent":number("relative_change_percent"),"start_period":model.get("start_period"),"end_period":model.get("end_period"),"start_value":number("start_value"),"end_value":number("end_value"),"trajectory_type":trajectory,"formula_expression":formula,"formula_language":FORMULA_LANGUAGE,"formula_variables":variables,"milestones":milestones,"lifecycle_status":lifecycle,"metadata":dict(model.get("metadata") or {})}
        digest=content_hash(normalized); now=utc_now(); existing=self.connection.execute("SELECT * FROM target_models WHERE target_model_id=?",(entity_id,)).fetchone()
        with self._registry_transaction():
            if existing:
                actual=int(existing["revision"])
                if expected_revision is not None and expected_revision!=actual: self._registry_concurrency("target_model",entity_id,int(expected_revision),actual)
                revision=actual+1
                self.connection.execute("""UPDATE target_models SET workspace_id=?,indicator_definition_id=?,name=?,target_type=?,unit_id=?,direction=?,target_value=?,lower_value=?,upper_value=?,relative_change_percent=?,start_period=?,end_period=?,start_value=?,end_value=?,trajectory_type=?,formula_expression=?,formula_language=?,milestones_json=?,lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE target_model_id=?""",
                  (workspace_id,indicator_definition_id,name,target_type,unit["unit_id"],direction,normalized["target_value"],normalized["lower_value"],normalized["upper_value"],normalized["relative_change_percent"],normalized["start_period"],normalized["end_period"],normalized["start_value"],normalized["end_value"],trajectory,formula,FORMULA_LANGUAGE,canonical_json(milestones),lifecycle,revision,now,canonical_json(normalized["metadata"]),entity_id)); action="update_target_model"
            else:
                if expected_revision not in (None,0): self._registry_concurrency("target_model",entity_id,int(expected_revision),0)
                revision=1
                self.connection.execute("""INSERT INTO target_models(target_model_id,workspace_id,indicator_definition_id,name,target_type,unit_id,direction,target_value,lower_value,upper_value,relative_change_percent,start_period,end_period,start_value,end_value,trajectory_type,formula_expression,formula_language,milestones_json,lifecycle_status,current_version,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (entity_id,workspace_id,indicator_definition_id,name,target_type,unit["unit_id"],direction,normalized["target_value"],normalized["lower_value"],normalized["upper_value"],normalized["relative_change_percent"],normalized["start_period"],normalized["end_period"],normalized["start_value"],normalized["end_value"],trajectory,formula,FORMULA_LANGUAGE,canonical_json(milestones),lifecycle,0,revision,str(model.get("created_at") or now),now,canonical_json(normalized["metadata"]))); action="create_target_model"
            version=self._versioned_record(table="target_models",id_field="target_model_id",entity_id=entity_id,version_table="target_model_versions",version_id_field="target_model_version_id",hash_field="model_hash",json_field="model_json",hash_value=digest,document=normalized,version_label=str(model.get("version_label") or model.get("version") or ""),actor=actor)
            self._audit(action,"target_model",entity_id,workspace_id=workspace_id,revision=revision,actor=actor,details={"version_id":version["target_model_version_id"],"model_hash":digest})
        return self.get_target_model(entity_id)

    def get_target_model(self,target_model_id:str)->Dict[str,Any]:
        row=self.connection.execute("SELECT * FROM target_models WHERE target_model_id=?",(target_model_id,)).fetchone()
        if not row: raise IndicatorRegistryError(f"target model not found: {target_model_id}")
        item=self._registry_decode(row,"milestones_json","metadata_json"); item["versions"]=[]
        for version in self.connection.execute("SELECT * FROM target_model_versions WHERE target_model_id=? ORDER BY version_number",(target_model_id,)).fetchall():
            decoded=dict(version); decoded["model"]=json.loads(decoded.pop("model_json")); item["versions"].append(decoded)
        return item

    def evaluate_target(self,target_model_id:str,*,baseline_value:Optional[float]=None,progress_fraction:Optional[float]=None,period_label:Optional[str]=None,variables:Optional[Dict[str,float]]=None)->Dict[str,Any]:
        model=self.get_target_model(target_model_id); target_type=model["target_type"]
        if target_type in {"absolute","threshold"}: value=float(model["target_value"]); result={"value":value}
        elif target_type=="range": result={"lower_value":float(model["lower_value"]),"upper_value":float(model["upper_value"])}
        elif target_type=="relative_change":
            if baseline_value is None: raise IndicatorRegistryError("relative-change target evaluation requires baseline_value")
            result={"value":float(baseline_value)*(1+float(model["relative_change_percent"])/100.0)}
        elif target_type=="formula":
            supplied=dict(variables or {}); supplied.setdefault("baseline",float(baseline_value or 0)); supplied.setdefault("current",0.0); supplied.setdefault("target",0.0); supplied.setdefault("period_index",0.0); supplied.setdefault("elapsed_periods",0.0); supplied.setdefault("observations_count",0.0); supplied.setdefault("sum_values",0.0); supplied.setdefault("mean_value",0.0); supplied.setdefault("minimum_value",0.0); supplied.setdefault("maximum_value",0.0)
            result={"value":evaluate_formula_expression(model["formula_expression"],supplied)}
        else:
            milestones=sorted(model["milestones"],key=lambda item:float(item.get("position",0)))
            if period_label:
                exact=next((item for item in milestones if str(item.get("period"))==period_label),None)
                if exact: result={"value":float(exact["value"]),"period":period_label}
                else: raise IndicatorRegistryError(f"target milestone not found for period: {period_label}")
            else:
                fraction=max(0.0,min(1.0,float(progress_fraction if progress_fraction is not None else 1.0)))
                start=float(model["start_value"] if model["start_value"] is not None else (milestones[0]["value"] if milestones else 0))
                end=float(model["end_value"] if model["end_value"] is not None else (milestones[-1]["value"] if milestones else model["target_value"] or start))
                trajectory=model["trajectory_type"]
                if trajectory=="step": value=start if fraction<1 else end
                elif trajectory=="exponential":
                    if start==0 or end/start<0: raise IndicatorRegistryError("exponential trajectory requires compatible non-zero endpoints")
                    value=start*((end/start)**fraction)
                elif trajectory=="custom":
                    supplied={"baseline":float(baseline_value or start),"current":start,"target":end,"period_index":fraction,"elapsed_periods":fraction,"observations_count":0.0,"sum_values":0.0,"mean_value":0.0,"minimum_value":0.0,"maximum_value":0.0}
                    value=evaluate_formula_expression(model["formula_expression"],supplied)
                else: value=start+(end-start)*fraction
                result={"value":value,"progress_fraction":fraction}
        unit=self.get_unit(model["unit_id"],workspace_id=model["workspace_id"])
        for key in ("value","lower_value","upper_value"):
            if key in result: result[key]=round(float(result[key]),int(unit["precision_digits"]))
        return {"target_model_id":target_model_id,"target_model_version_id":model["versions"][-1]["target_model_version_id"],"unit_id":unit["unit_id"],"target_type":target_type,**result}

    def register_method_definition(self,method:Dict[str,Any],*,workspace_id:str,expected_revision:Optional[int]=None,actor:str="system")->Dict[str,Any]:
        name=str(method.get("name") or "").strip()
        if not name: raise IndicatorRegistryError("method name is required")
        kind=str(method.get("method_kind") or "measurement"); design=str(method.get("design_type") or "monitoring")
        if kind not in METHOD_KINDS: raise IndicatorRegistryError(f"unsupported method kind: {kind}")
        if design not in METHOD_DESIGN_TYPES: raise IndicatorRegistryError(f"unsupported design type: {design}")
        formula=str(method.get("formula_expression") or "").strip(); variables=validate_formula_expression(formula)
        entity_id=str(method.get("method_definition_id") or method.get("id") or registry_id("method-definition",workspace_id,name.casefold()))
        lifecycle=str(method.get("lifecycle_status") or "draft")
        normalized={"method_definition_id":entity_id,"workspace_id":workspace_id,"name":name,"method_kind":kind,"design_type":design,"description":str(method.get("description") or ""),"formula_expression":formula,"formula_language":FORMULA_LANGUAGE,"formula_variables":variables,"input_requirements":list(method.get("input_requirements") or []),"quality_profile":dict(method.get("quality_profile") or {"reproducibility":"not_assessed","data_quality":"not_assessed","review_status":"not_assessed"}),"limitations":list(method.get("limitations") or []),"lifecycle_status":lifecycle,"metadata":dict(method.get("metadata") or {})}
        digest=content_hash(normalized); now=utc_now(); existing=self.connection.execute("SELECT * FROM method_definitions WHERE method_definition_id=?",(entity_id,)).fetchone()
        with self._registry_transaction():
            if existing:
                actual=int(existing["revision"])
                if expected_revision is not None and expected_revision!=actual: self._registry_concurrency("method_definition",entity_id,int(expected_revision),actual)
                revision=actual+1
                self.connection.execute("""UPDATE method_definitions SET workspace_id=?,name=?,method_kind=?,design_type=?,description=?,formula_expression=?,formula_language=?,input_requirements_json=?,quality_profile_json=?,limitations_json=?,lifecycle_status=?,revision=?,updated_at=?,metadata_json=? WHERE method_definition_id=?""",
                  (workspace_id,name,kind,design,normalized["description"],formula,FORMULA_LANGUAGE,canonical_json(normalized["input_requirements"]),canonical_json(normalized["quality_profile"]),canonical_json(normalized["limitations"]),lifecycle,revision,now,canonical_json(normalized["metadata"]),entity_id)); action="update_method_definition"
            else:
                if expected_revision not in (None,0): self._registry_concurrency("method_definition",entity_id,int(expected_revision),0)
                revision=1
                self.connection.execute("""INSERT INTO method_definitions(method_definition_id,workspace_id,name,method_kind,design_type,description,formula_expression,formula_language,input_requirements_json,quality_profile_json,limitations_json,lifecycle_status,current_version,revision,created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (entity_id,workspace_id,name,kind,design,normalized["description"],formula,FORMULA_LANGUAGE,canonical_json(normalized["input_requirements"]),canonical_json(normalized["quality_profile"]),canonical_json(normalized["limitations"]),lifecycle,0,revision,str(method.get("created_at") or now),now,canonical_json(normalized["metadata"]))); action="create_method_definition"
            version=self._versioned_record(table="method_definitions",id_field="method_definition_id",entity_id=entity_id,version_table="method_definition_versions",version_id_field="method_definition_version_id",hash_field="method_hash",json_field="method_json",hash_value=digest,document=normalized,version_label=str(method.get("version_label") or method.get("version") or ""),actor=actor)
            self._audit(action,"method_definition",entity_id,workspace_id=workspace_id,revision=revision,actor=actor,details={"version_id":version["method_definition_version_id"],"method_hash":digest})
        return self.get_method_definition(entity_id)

    def get_method_definition(self,method_definition_id:str)->Dict[str,Any]:
        row=self.connection.execute("SELECT * FROM method_definitions WHERE method_definition_id=?",(method_definition_id,)).fetchone()
        if not row: raise IndicatorRegistryError(f"method definition not found: {method_definition_id}")
        item=self._registry_decode(row,"input_requirements_json","quality_profile_json","limitations_json","metadata_json"); item["versions"]=[]
        for version in self.connection.execute("SELECT * FROM method_definition_versions WHERE method_definition_id=? ORDER BY version_number",(method_definition_id,)).fetchall():
            decoded=dict(version); decoded["method"]=json.loads(decoded.pop("method_json")); item["versions"].append(decoded)
        return item

    def bind_indicator_registry(self,*,workspace_id:str,initiative_id:str,indicator_id:str,indicator_definition_id:str,baseline_model_id:Optional[str]=None,target_model_id:Optional[str]=None,method_definition_id:Optional[str]=None,actor:str="system",metadata:Optional[Dict[str,Any]]=None)->Dict[str,Any]:
        indicator=self.get_indicator_definition(indicator_definition_id); unit=self.get_unit(indicator["unit_id"],workspace_id=workspace_id)
        baseline=self.get_baseline_model(baseline_model_id) if baseline_model_id else None
        target=self.get_target_model(target_model_id) if target_model_id else None
        method=self.get_method_definition(method_definition_id) if method_definition_id else None
        for record,label in ((baseline,"baseline"),(target,"target")):
            if record:
                record_unit=self.get_unit(record["unit_id"],workspace_id=workspace_id)
                if record_unit["dimension"]!=unit["dimension"]: raise UnitCompatibilityError(f"{label} model unit is incompatible with indicator unit")
        binding_id=registry_id("indicator-binding",initiative_id,indicator_id); now=utc_now()
        current=self.connection.execute("SELECT * FROM indicator_registry_bindings WHERE binding_id=?",(binding_id,)).fetchone(); revision=int(current["revision"])+1 if current else 1
        values=(binding_id,workspace_id,initiative_id,indicator_id,indicator_definition_id,indicator["versions"][-1]["indicator_definition_version_id"],unit["unit_id"],baseline_model_id,baseline["versions"][-1]["baseline_model_version_id"] if baseline else None,target_model_id,target["versions"][-1]["target_model_version_id"] if target else None,method_definition_id,method["versions"][-1]["method_definition_version_id"] if method else None,now,actor,revision,canonical_json(metadata or {}))
        with self._registry_transaction():
            self.connection.execute("""INSERT INTO indicator_registry_bindings(binding_id,workspace_id,initiative_id,indicator_id,indicator_definition_id,indicator_definition_version_id,unit_id,baseline_model_id,baseline_model_version_id,target_model_id,target_model_version_id,method_definition_id,method_definition_version_id,bound_at,bound_by,revision,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(binding_id) DO UPDATE SET indicator_definition_id=excluded.indicator_definition_id,indicator_definition_version_id=excluded.indicator_definition_version_id,unit_id=excluded.unit_id,baseline_model_id=excluded.baseline_model_id,baseline_model_version_id=excluded.baseline_model_version_id,target_model_id=excluded.target_model_id,target_model_version_id=excluded.target_model_version_id,method_definition_id=excluded.method_definition_id,method_definition_version_id=excluded.method_definition_version_id,bound_at=excluded.bound_at,bound_by=excluded.bound_by,revision=excluded.revision,metadata_json=excluded.metadata_json""",values)
            self._audit("bind_indicator_registry","indicator",indicator_id,workspace_id=workspace_id,initiative_id=initiative_id,revision=revision,actor=actor,details={"binding_id":binding_id})
        return self._registry_decode(self.connection.execute("SELECT * FROM indicator_registry_bindings WHERE binding_id=?",(binding_id,)).fetchone(),"metadata_json")

    def _materialize_contract_registry(self,contract:Dict[str,Any],*,actor:str)->None:
        facts=contract["facts"]; workspace_id=facts["workspace"]["id"]; initiative_id=facts["initiative"]["id"]
        indicator=facts["indicator"]; definition=indicator["definition_version"]; measurement=facts["measurement"]
        unit_code=str(definition.get("unit") or measurement.get("baseline",{}).get("unit") or "count")
        try: unit=self.get_unit(unit_code,workspace_id=workspace_id)
        except IndicatorRegistryError:
            unit=self.register_unit({"code":unit_code,"name":unit_code,"dimension":"custom","metadata":{"materialized_from_contract":contract["record_id"]}},workspace_id=workspace_id,actor=actor)
        indicator_definition=self.register_indicator_definition({"indicator_definition_id":registry_id("indicator-definition",workspace_id,indicator["name"].casefold()),"name":indicator["name"],"description":definition.get("name",""),"direction":definition.get("direction","higher_is_better"),"unit_id":unit["unit_id"],"aggregation_method":"latest","version_label":definition.get("version","1.0"),"lifecycle_status":"active","metadata":{"canonical_indicator_id":indicator["id"],"canonical_definition_version_id":definition["id"],"record_id":contract["record_id"]}},workspace_id=workspace_id,actor=actor)
        baseline=facts["measurement"]["baseline"]
        baseline_model=self.register_baseline_model({"baseline_model_id":registry_id("baseline-model",workspace_id,indicator["id"]),"name":f"{indicator['name']} entered baseline","method_type":"benchmark","unit_id":unit["unit_id"],"benchmark_value":baseline.get("value"),"period_start":(baseline.get("period") or {}).get("label"),"period_end":(baseline.get("period") or {}).get("label"),"confidence":"medium","lifecycle_status":"active","version_label":contract.get("contract_version",""),"parameters":{"canonical_baseline_id":baseline["id"]},"metadata":{"record_id":contract["record_id"]}},workspace_id=workspace_id,actor=actor)
        target=facts["measurement"]["target"]
        target_model=self.register_target_model({"target_model_id":registry_id("target-model",workspace_id,indicator["id"]),"indicator_definition_id":indicator_definition["indicator_definition_id"],"name":f"{indicator['name']} target","target_type":"absolute","unit_id":unit["unit_id"],"direction":target.get("direction",definition.get("direction","higher_is_better")),"target_value":target.get("value"),"end_period":(target.get("period") or {}).get("label"),"lifecycle_status":"active","version_label":contract.get("contract_version",""),"metadata":{"canonical_target_id":target["id"],"record_id":contract["record_id"]}},workspace_id=workspace_id,actor=actor)
        canonical_method=(facts.get("methods") or [{}])[0]
        method_definition=None
        if canonical_method:
            method_definition=self.register_method_definition({"method_definition_id":canonical_method.get("id"),"name":canonical_method.get("name","Entered measurement method"),"method_kind":"measurement","design_type":canonical_method.get("design_type","monitoring"),"description":canonical_method.get("description",""),"version_label":canonical_method.get("version","1.0"),"lifecycle_status":"active","quality_profile":{"reproducibility":"documented" if len(str(canonical_method.get("description") or ""))>=80 else "partial","data_quality":"not_assessed","review_status":contract.get("lifecycle_status","draft")},"limitations":[],"metadata":{"canonical_method_id":canonical_method.get("id"),"record_id":contract["record_id"]}},workspace_id=workspace_id,actor=actor)
        self.bind_indicator_registry(workspace_id=workspace_id,initiative_id=initiative_id,indicator_id=indicator["id"],indicator_definition_id=indicator_definition["indicator_definition_id"],baseline_model_id=baseline_model["baseline_model_id"],target_model_id=target_model["target_model_id"],method_definition_id=method_definition["method_definition_id"] if method_definition else None,actor=actor,metadata={"materialized_from_contract":contract["record_id"]})

    def export_indicator_registry(self,workspace_id:str)->Dict[str,Any]:
        units=[self._registry_decode(row,"metadata_json") for row in self.connection.execute("SELECT * FROM unit_definitions WHERE workspace_id IS NULL OR workspace_id=? ORDER BY dimension,code",(workspace_id,)).fetchall()]
        indicators=[self.get_indicator_definition(row["indicator_definition_id"]) for row in self.connection.execute("SELECT indicator_definition_id FROM indicator_definitions WHERE workspace_id=? ORDER BY name",(workspace_id,)).fetchall()]
        baselines=[self.get_baseline_model(row["baseline_model_id"]) for row in self.connection.execute("SELECT baseline_model_id FROM baseline_models WHERE workspace_id=? ORDER BY name",(workspace_id,)).fetchall()]
        targets=[self.get_target_model(row["target_model_id"]) for row in self.connection.execute("SELECT target_model_id FROM target_models WHERE workspace_id=? ORDER BY name",(workspace_id,)).fetchall()]
        methods=[self.get_method_definition(row["method_definition_id"]) for row in self.connection.execute("SELECT method_definition_id FROM method_definitions WHERE workspace_id=? ORDER BY name",(workspace_id,)).fetchall()]
        bindings=[self._registry_decode(row,"metadata_json") for row in self.connection.execute("SELECT * FROM indicator_registry_bindings WHERE workspace_id=? ORDER BY initiative_id,indicator_id",(workspace_id,)).fetchall()]
        unit_ids={item["unit_id"] for item in units}; indicator_ids={item["indicator_definition_id"] for item in indicators}; baseline_ids={item["baseline_model_id"] for item in baselines}; target_ids={item["target_model_id"] for item in targets}; method_ids={item["method_definition_id"] for item in methods}
        missing_units=sorted({item["unit_id"] for item in [*indicators,*baselines,*targets] if item["unit_id"] not in unit_ids})
        orphan_bindings=[]
        for item in bindings:
            if item["indicator_definition_id"] not in indicator_ids or (item.get("baseline_model_id") and item["baseline_model_id"] not in baseline_ids) or (item.get("target_model_id") and item["target_model_id"] not in target_ids) or (item.get("method_definition_id") and item["method_definition_id"] not in method_ids): orphan_bindings.append(item["binding_id"])
        return {"registry_type":"global_impact_indicator_registry","registry_version":REGISTRY_VERSION,"workspace_id":workspace_id,"generated_at":utc_now(),"units":units,"indicator_definitions":indicators,"baseline_models":baselines,"target_models":targets,"method_definitions":methods,"bindings":bindings,"integrity":{"valid":not missing_units and not orphan_bindings,"unit_count":len(units),"indicator_definition_count":len(indicators),"indicator_definition_version_count":sum(len(item["versions"]) for item in indicators),"baseline_model_count":len(baselines),"target_model_count":len(targets),"method_definition_count":len(methods),"binding_count":len(bindings),"missing_unit_ids":missing_units,"orphan_binding_ids":orphan_bindings}}

    def _restore_indicator_registry(self,registry:Dict[str,Any],*,actor:str="restore")->None:
        if not registry: return
        workspace_id=registry["workspace_id"]
        # Global standard units are seeded by migrations; custom and updated units are restored explicitly.
        for unit in registry.get("units",[]):
            if unit.get("workspace_id") is not None:
                self.register_unit(unit,workspace_id=unit.get("workspace_id"),actor=actor)
        for indicator in registry.get("indicator_definitions",[]):
            record=dict(indicator); versions=record.pop("versions",[])
            self.register_indicator_definition(record,workspace_id=workspace_id,actor=actor)
            # The latest normalized record is sufficient; immutable historical rows are restored below.
            for version in versions:
                self.connection.execute("INSERT OR IGNORE INTO indicator_definition_versions(indicator_definition_version_id,indicator_definition_id,version_number,version_label,effective_from,effective_through,definition_hash,definition_json,created_at,created_by) VALUES (?,?,?,?,?,?,?,?,?,?)",(version["indicator_definition_version_id"],version["indicator_definition_id"],version["version_number"],version["version_label"],version.get("effective_from"),version.get("effective_through"),version["definition_hash"],canonical_json(version["definition"]),version["created_at"],version["created_by"]))
        for model in registry.get("baseline_models",[]):
            record=dict(model); versions=record.pop("versions",[])
            self.register_baseline_model(record,workspace_id=workspace_id,actor=actor)
            for version in versions:
                self.connection.execute("INSERT OR IGNORE INTO baseline_model_versions(baseline_model_version_id,baseline_model_id,version_number,version_label,model_hash,model_json,created_at,created_by) VALUES (?,?,?,?,?,?,?,?)",(version["baseline_model_version_id"],version["baseline_model_id"],version["version_number"],version["version_label"],version["model_hash"],canonical_json(version["model"]),version["created_at"],version["created_by"]))
        for model in registry.get("target_models",[]):
            record=dict(model); versions=record.pop("versions",[])
            self.register_target_model(record,workspace_id=workspace_id,actor=actor)
            for version in versions:
                self.connection.execute("INSERT OR IGNORE INTO target_model_versions(target_model_version_id,target_model_id,version_number,version_label,model_hash,model_json,created_at,created_by) VALUES (?,?,?,?,?,?,?,?)",(version["target_model_version_id"],version["target_model_id"],version["version_number"],version["version_label"],version["model_hash"],canonical_json(version["model"]),version["created_at"],version["created_by"]))
        for method in registry.get("method_definitions",[]):
            record=dict(method); versions=record.pop("versions",[])
            self.register_method_definition(record,workspace_id=workspace_id,actor=actor)
            for version in versions:
                self.connection.execute("INSERT OR IGNORE INTO method_definition_versions(method_definition_version_id,method_definition_id,version_number,version_label,method_hash,method_json,created_at,created_by) VALUES (?,?,?,?,?,?,?,?)",(version["method_definition_version_id"],version["method_definition_id"],version["version_number"],version["version_label"],version["method_hash"],canonical_json(version["method"]),version["created_at"],version["created_by"]))
        for binding in registry.get("bindings",[]):
            self.bind_indicator_registry(workspace_id=binding["workspace_id"],initiative_id=binding["initiative_id"],indicator_id=binding["indicator_id"],indicator_definition_id=binding["indicator_definition_id"],baseline_model_id=binding.get("baseline_model_id"),target_model_id=binding.get("target_model_id"),method_definition_id=binding.get("method_definition_id"),actor=actor,metadata=binding.get("metadata") or {})
