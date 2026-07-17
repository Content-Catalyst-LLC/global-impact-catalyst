"""Governed trends, comparisons, scenarios, uncertainty, and sensitivity.

Global Impact Catalyst v1.7.0 adds an analytical repository over governed
observations and registry records. Results are descriptive/planning artifacts,
not assurance, certification, causal proof, or automatic truth verification.
"""
from __future__ import annotations

import hashlib
import json
import math
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

ANALYSIS_VERSION = "1.7.0"
BENCHMARK_TYPES = {"external", "peer", "historical", "target", "standard", "portfolio"}
QUALITY_STATUSES = {"not_assessed", "weak", "adequate", "strong", "verified"}
LIFECYCLE_STATUSES = {"draft", "active", "deprecated", "archived"}
SCENARIO_TYPES = {"projection", "counterfactual", "stress", "optimistic", "pessimistic", "planning"}
SCENARIO_MODELS = {"constant", "linear", "compound", "step"}
UNCERTAINTY_TYPES = {"absolute", "relative", "bounds", "combined"}
DISTRIBUTIONS = {"bounded", "normal_assumption", "triangular_assumption", "unknown"}
PERIOD_POLICIES = {"exact", "overlap", "same_label", "ignore"}
CONTEXT_POLICIES = {"exact", "warn", "ignore"}
MISSING_POLICIES = {"block", "exclude", "warn"}
PARTIAL_POLICIES = {"block", "include", "exclude"}
DIRECTIONS = {"higher_is_better", "lower_is_better", "neutral"}


class AnalysisError(RuntimeError):
    """Base analytical repository error."""


class ComparisonGuardError(AnalysisError):
    """Raised when a comparison cannot satisfy its declared policy."""


class ScenarioEvaluationError(AnalysisError):
    """Raised when a scenario cannot be evaluated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def analysis_id(kind: str, *parts: Any) -> str:
    material = "|".join(canonical_json(part) if isinstance(part, (dict, list)) else str(part) for part in parts)
    return f"gic-{kind}-{hashlib.sha256(material.encode('utf-8')).hexdigest()[:20]}"


def finite(value: Any, name: str, *, allow_none: bool = False) -> Optional[float]:
    if value in (None, ""):
        if allow_none:
            return None
        raise AnalysisError(f"{name} is required")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise AnalysisError(f"{name} must be numeric") from exc
    if not math.isfinite(number):
        raise AnalysisError(f"{name} must be finite")
    return number


def _round(value: Optional[float]) -> Optional[float]:
    return None if value is None else round(float(value), 6)


def _period_overlap(left: Dict[str, Any], right: Dict[str, Any]) -> bool:
    if left.get("period_start") and right.get("period_end") and left["period_start"] > right["period_end"]:
        return False
    if left.get("period_end") and right.get("period_start") and left["period_end"] < right["period_start"]:
        return False
    return True


def _period_matches(left: Dict[str, Any], right: Dict[str, Any], policy: str) -> bool:
    if policy == "ignore":
        return True
    if policy == "same_label":
        return bool(left.get("period_label")) and left.get("period_label") == right.get("period_label")
    if policy == "exact":
        return (
            left.get("period_start") == right.get("period_start")
            and left.get("period_end") == right.get("period_end")
            and (not left.get("period_label") or not right.get("period_label") or left.get("period_label") == right.get("period_label"))
        )
    return _period_overlap(left, right)


def _slope(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    x_mean = (len(values) - 1) / 2.0
    y_mean = sum(values) / len(values)
    numerator = sum((index - x_mean) * (value - y_mean) for index, value in enumerate(values))
    denominator = sum((index - x_mean) ** 2 for index in range(len(values)))
    return 0.0 if denominator == 0 else numerator / denominator


class AnalysisScenarioMixin:
    """SQLite mixin for v1.7.0 analysis records."""

    @contextmanager
    def _analysis_transaction(self) -> Iterator[Any]:
        if self.connection.in_transaction:
            yield self.connection
        else:
            with self.transaction() as connection:
                yield connection

    @staticmethod
    def _analysis_decode(row: Any, *json_fields: str) -> Dict[str, Any]:
        item = dict(row)
        for field in json_fields:
            if field in item:
                item[field.removesuffix("_json")] = json.loads(item.pop(field) or "{}")
        return item

    def _analysis_concurrency(self, entity_type: str, entity_id: str, expected: int, actual: int) -> None:
        try:
            from python.global_impact_repository import OptimisticConcurrencyError
            raise OptimisticConcurrencyError(entity_type, entity_id, expected, actual)
        except ImportError as exc:
            raise AnalysisError(f"stale {entity_type} revision for {entity_id}: expected {expected}, current {actual}") from exc

    def _record_analysis_run(
        self, analysis_type: str, subject_id: str, result: Dict[str, Any], *, workspace_id: str,
        initiative_id: Optional[str] = None, input_document: Optional[Dict[str, Any]] = None,
        actor: str = "system", metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        created_at = utc_now()
        input_hash = content_hash(input_document or {})
        result_hash = content_hash(result)
        run_id = analysis_id("analysis-run", workspace_id, analysis_type, subject_id, input_hash, result_hash)
        with self._analysis_transaction():
            self.connection.execute(
                """INSERT OR IGNORE INTO analysis_runs(analysis_run_id,workspace_id,initiative_id,analysis_type,
                   subject_id,input_hash,result_hash,result_json,created_by,created_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (run_id, workspace_id, initiative_id, analysis_type, subject_id, input_hash, result_hash,
                 canonical_json(result), actor, created_at, canonical_json(metadata or {})),
            )
            self._audit("record_analysis_run", "analysis_run", run_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, actor=actor,
                        details={"analysis_type": analysis_type, "subject_id": subject_id, "result_hash": result_hash})
        result = dict(result)
        result["analysis_run_id"] = run_id
        return result

    def get_analysis_run(self, analysis_run_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM analysis_runs WHERE analysis_run_id=?", (analysis_run_id,)).fetchone()
        if not row:
            raise AnalysisError(f"analysis run not found: {analysis_run_id}")
        return self._analysis_decode(row, "result_json", "metadata_json")

    def list_analysis_runs(self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None,
                           analysis_type: Optional[str] = None, subject_id: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses = ["1=1"]
        params: List[Any] = []
        for field, value in (("workspace_id", workspace_id), ("initiative_id", initiative_id),
                             ("analysis_type", analysis_type), ("subject_id", subject_id)):
            if value is not None:
                clauses.append(f"{field}=?")
                params.append(value)
        rows = self.connection.execute(
            f"SELECT * FROM analysis_runs WHERE {' AND '.join(clauses)} ORDER BY created_at,analysis_run_id", params
        ).fetchall()
        return [self._analysis_decode(row, "result_json", "metadata_json") for row in rows]

    def analyze_trend(self, initiative_id: str, indicator_id: str, *, target_unit_id: Optional[str] = None,
                      include_partial: bool = False, missing_policy: str = "exclude", actor: str = "system",
                      persist: bool = False) -> Dict[str, Any]:
        if missing_policy not in MISSING_POLICIES:
            raise AnalysisError(f"unsupported missing policy: {missing_policy}")
        records = self.list_observations(initiative_id=initiative_id, indicator_id=indicator_id)
        effective = self._effective_records(records, "observation_record_id")
        contract = self.get_contract(initiative_id=initiative_id)
        workspace_id = contract["workspace_id"]
        target_unit = target_unit_id or next((item["unit_id"] for item in effective if item.get("value") is not None), None)
        points: List[Dict[str, Any]] = []
        excluded: List[Dict[str, Any]] = []
        blockers: List[str] = []
        warnings: List[str] = []
        for item in effective:
            if item["data_state"] == "missing" or item.get("value") is None:
                excluded.append({"observation_record_id": item["observation_record_id"], "reason": "missing_data"})
                if missing_policy == "block": blockers.append(f"missing observation blocks trend: {item['observation_record_id']}")
                elif missing_policy == "warn": warnings.append(f"missing observation excluded: {item['observation_record_id']}")
                continue
            if item["data_state"] == "partial" and not include_partial:
                excluded.append({"observation_record_id": item["observation_record_id"], "reason": "partial_data"})
                warnings.append(f"partial observation excluded: {item['observation_record_id']}")
                continue
            value = float(item["value"])
            if target_unit and item["unit_id"] != target_unit:
                try:
                    value = self.convert_value(value, item["unit_id"], target_unit, workspace_id=workspace_id)
                except Exception as exc:
                    blockers.append(f"unit conversion failed for {item['observation_record_id']}: {exc}")
                    excluded.append({"observation_record_id": item["observation_record_id"], "reason": "incompatible_unit"})
                    continue
            points.append({
                "observation_record_id": item["observation_record_id"], "period_start": item.get("period_start"),
                "period_end": item.get("period_end"), "period_label": item.get("period_label") or "",
                "value": _round(value), "unit_id": target_unit or item["unit_id"], "data_state": item["data_state"],
                "dimensions": item.get("dimensions") or {},
            })
        points.sort(key=lambda item: (item.get("period_start") or item.get("period_label") or "", item["observation_record_id"]))
        values = [float(item["value"]) for item in points]
        first = values[0] if values else None
        last = values[-1] if values else None
        change = None if first is None or last is None else last - first
        slope = _slope(values)
        if len(values) < 2:
            warnings.append("at least two usable observations are required for a directional trend")
        direction = "increasing" if slope > 1e-12 else "decreasing" if slope < -1e-12 else "stable"
        result = {
            "analysis_type": "trend", "analysis_version": ANALYSIS_VERSION, "workspace_id": workspace_id,
            "initiative_id": initiative_id, "indicator_id": indicator_id, "unit_id": target_unit,
            "points": points, "excluded": excluded,
            "statistics": {"count": len(values), "first_value": _round(first), "last_value": _round(last),
                           "absolute_change": _round(change),
                           "percent_change": None if change is None or first == 0 else _round(change / abs(first) * 100),
                           "slope": _round(slope), "direction": direction,
                           "minimum": _round(min(values)) if values else None, "maximum": _round(max(values)) if values else None,
                           "mean": _round(sum(values) / len(values)) if values else None},
            "integrity": {"valid": not blockers and len(values) >= 1, "included_count": len(points),
                          "excluded_count": len(excluded), "blockers": blockers, "warnings": warnings},
            "boundary": "Trend statistics describe selected observations and do not establish causality or attribution.",
        }
        if persist:
            return self._record_analysis_run("trend", indicator_id, result, workspace_id=workspace_id,
                                             initiative_id=initiative_id,
                                             input_document={"target_unit_id": target_unit_id, "include_partial": include_partial,
                                                             "missing_policy": missing_policy}, actor=actor)
        return result

    def register_benchmark(self, benchmark: Dict[str, Any], *, workspace_id: str,
                           expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        name = str(benchmark.get("name") or "").strip()
        indicator_id = str(benchmark.get("indicator_id") or "").strip()
        if not name or not indicator_id:
            raise AnalysisError("benchmark name and indicator_id are required")
        benchmark_type = str(benchmark.get("benchmark_type") or "external")
        quality = str(benchmark.get("quality_status") or "not_assessed")
        lifecycle = str(benchmark.get("lifecycle_status") or "draft")
        if benchmark_type not in BENCHMARK_TYPES: raise AnalysisError(f"unsupported benchmark type: {benchmark_type}")
        if quality not in QUALITY_STATUSES: raise AnalysisError(f"unsupported benchmark quality status: {quality}")
        if lifecycle not in LIFECYCLE_STATUSES: raise AnalysisError(f"unsupported lifecycle status: {lifecycle}")
        value = finite(benchmark.get("value"), "benchmark value")
        unit = self.get_unit(str(benchmark.get("unit_id") or benchmark.get("unit") or "count"), workspace_id=workspace_id)
        entity_id = str(benchmark.get("benchmark_id") or benchmark.get("id") or analysis_id(
            "benchmark", workspace_id, indicator_id, name.casefold(), benchmark.get("period_label") or ""
        ))
        existing = self.connection.execute("SELECT * FROM analysis_benchmarks WHERE benchmark_id=?", (entity_id,)).fetchone()
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and int(expected_revision) != actual:
                self._analysis_concurrency("benchmark", entity_id, int(expected_revision), actual)
            revision, created_at = actual + 1, existing["created_at"]
        else:
            if expected_revision not in (None, 0): self._analysis_concurrency("benchmark", entity_id, int(expected_revision), 0)
            revision, created_at = 1, str(benchmark.get("created_at") or utc_now())
        now = utc_now()
        with self._analysis_transaction():
            self.connection.execute(
                """INSERT INTO analysis_benchmarks(benchmark_id,workspace_id,indicator_id,indicator_definition_id,name,
                   benchmark_type,value,unit_id,period_start,period_end,period_label,geography,population,source_id,
                   method_definition_id,quality_status,lifecycle_status,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(benchmark_id) DO UPDATE SET indicator_id=excluded.indicator_id,
                   indicator_definition_id=excluded.indicator_definition_id,name=excluded.name,benchmark_type=excluded.benchmark_type,
                   value=excluded.value,unit_id=excluded.unit_id,period_start=excluded.period_start,period_end=excluded.period_end,
                   period_label=excluded.period_label,geography=excluded.geography,population=excluded.population,
                   source_id=excluded.source_id,method_definition_id=excluded.method_definition_id,
                   quality_status=excluded.quality_status,lifecycle_status=excluded.lifecycle_status,revision=excluded.revision,
                   updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (entity_id, workspace_id, indicator_id, benchmark.get("indicator_definition_id"), name, benchmark_type,
                 value, unit["unit_id"], benchmark.get("period_start"), benchmark.get("period_end"),
                 str(benchmark.get("period_label") or ""), str(benchmark.get("geography") or ""),
                 str(benchmark.get("population") or ""), benchmark.get("source_id"), benchmark.get("method_definition_id"),
                 quality, lifecycle, revision, created_at, now, canonical_json(benchmark.get("metadata") or {})),
            )
            self._audit("register_benchmark", "analysis_benchmark", entity_id, workspace_id=workspace_id,
                        revision=revision, actor=actor, details={"indicator_id": indicator_id})
        return self.get_benchmark(entity_id)

    def get_benchmark(self, benchmark_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM analysis_benchmarks WHERE benchmark_id=?", (benchmark_id,)).fetchone()
        if not row: raise AnalysisError(f"benchmark not found: {benchmark_id}")
        return self._analysis_decode(row, "metadata_json")

    def list_benchmarks(self, *, workspace_id: Optional[str] = None, indicator_id: Optional[str] = None,
                        lifecycle_status: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses, params = ["1=1"], []
        for field, value in (("workspace_id", workspace_id), ("indicator_id", indicator_id),
                             ("lifecycle_status", lifecycle_status)):
            if value is not None: clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(f"SELECT * FROM analysis_benchmarks WHERE {' AND '.join(clauses)} ORDER BY name,benchmark_id", params).fetchall()
        return [self._analysis_decode(row, "metadata_json") for row in rows]

    @staticmethod
    def _guard_context(name: str, left: str, right: str, policy: str, blockers: List[str], warnings: List[str]) -> None:
        if policy == "ignore" or not left or not right or left == right: return
        message = f"{name} differs: {left!r} versus {right!r}"
        (blockers if policy == "exact" else warnings).append(message)

    def _choose_observation(self, initiative_id: str, indicator_id: str, *, observation_id: Optional[str] = None,
                            benchmark: Optional[Dict[str, Any]] = None, period_policy: str = "overlap") -> Optional[Dict[str, Any]]:
        records = self._effective_records(self.list_observations(initiative_id=initiative_id, indicator_id=indicator_id), "observation_record_id")
        records = [item for item in records if item["data_state"] != "missing" and item.get("value") is not None]
        if observation_id:
            return next((item for item in records if item["observation_record_id"] == observation_id), None)
        if benchmark and period_policy != "ignore":
            matches = [item for item in records if _period_matches(item, benchmark, period_policy)]
            if matches: records = matches
        records.sort(key=lambda item: (item.get("period_start") or item.get("period_label") or "", item.get("received_at") or ""))
        return records[-1] if records else None

    def compare_to_benchmark(self, initiative_id: str, indicator_id: str, benchmark_id: str, *,
                             observation_id: Optional[str] = None, period_policy: str = "overlap",
                             observation_geography: str = "", observation_population: str = "",
                             geography_policy: str = "warn", population_policy: str = "warn",
                             direction: str = "neutral", actor: str = "system", persist: bool = False) -> Dict[str, Any]:
        if period_policy not in PERIOD_POLICIES: raise AnalysisError(f"unsupported period policy: {period_policy}")
        if geography_policy not in CONTEXT_POLICIES or population_policy not in CONTEXT_POLICIES:
            raise AnalysisError("unsupported comparison context policy")
        if direction not in DIRECTIONS: raise AnalysisError(f"unsupported comparison direction: {direction}")
        benchmark = self.get_benchmark(benchmark_id)
        observation = self._choose_observation(initiative_id, indicator_id, observation_id=observation_id,
                                               benchmark=benchmark, period_policy=period_policy)
        blockers: List[str] = []
        warnings: List[str] = []
        if not observation:
            blockers.append("no usable observation satisfies the selected period policy")
            value = None
        else:
            value = float(observation["value"])
            if observation["unit_id"] != benchmark["unit_id"]:
                try: value = self.convert_value(value, observation["unit_id"], benchmark["unit_id"], workspace_id=benchmark["workspace_id"])
                except Exception as exc: blockers.append(f"unit incompatibility: {exc}")
        self._guard_context("geography", observation_geography, benchmark.get("geography") or "", geography_policy, blockers, warnings)
        self._guard_context("population", observation_population, benchmark.get("population") or "", population_policy, blockers, warnings)
        difference = None if value is None else value - float(benchmark["value"])
        relation = None if difference is None else "above" if difference > 0 else "below" if difference < 0 else "equal"
        favorable = None
        if difference is not None and direction != "neutral":
            favorable = difference >= 0 if direction == "higher_is_better" else difference <= 0
        result = {
            "analysis_type": "benchmark_comparison", "analysis_version": ANALYSIS_VERSION,
            "workspace_id": benchmark["workspace_id"], "initiative_id": initiative_id, "indicator_id": indicator_id,
            "benchmark": benchmark, "observation": observation,
            "comparison": {"observation_value": _round(value), "benchmark_value": _round(benchmark["value"]),
                           "difference": _round(difference),
                           "percent_difference": None if difference is None or benchmark["value"] == 0 else _round(difference / abs(float(benchmark["value"])) * 100),
                           "relation": relation, "direction": direction, "favorable": favorable, "unit_id": benchmark["unit_id"]},
            "policy": {"period_policy": period_policy, "geography_policy": geography_policy,
                       "population_policy": population_policy},
            "integrity": {"valid": not blockers, "blockers": blockers, "warnings": warnings},
            "boundary": "Benchmark comparison is descriptive and does not establish causality, attribution, or assurance.",
        }
        if persist:
            return self._record_analysis_run("benchmark_comparison", benchmark_id, result,
                                             workspace_id=benchmark["workspace_id"], initiative_id=initiative_id,
                                             input_document={"observation_id": observation_id, "period_policy": period_policy,
                                                             "geography_policy": geography_policy, "population_policy": population_policy,
                                                             "direction": direction}, actor=actor)
        return result

    def create_comparison_set(self, comparison_set: Dict[str, Any], *, workspace_id: str,
                              expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        name = str(comparison_set.get("name") or "").strip()
        indicator_id = str(comparison_set.get("indicator_id") or "").strip()
        if not name or not indicator_id: raise AnalysisError("comparison set name and indicator_id are required")
        policy = {"period_policy": "same_label", "geography_policy": "warn", "population_policy": "warn",
                  "missing_policy": "exclude", "partial_policy": "exclude", "direction": "neutral"}
        policy.update(dict(comparison_set.get("comparison_policy") or {}))
        if policy["period_policy"] not in PERIOD_POLICIES or policy["geography_policy"] not in CONTEXT_POLICIES or policy["population_policy"] not in CONTEXT_POLICIES or policy["missing_policy"] not in MISSING_POLICIES or policy["partial_policy"] not in PARTIAL_POLICIES or policy["direction"] not in DIRECTIONS:
            raise AnalysisError("comparison set contains unsupported policy values")
        entity_id = str(comparison_set.get("comparison_set_id") or comparison_set.get("id") or analysis_id("comparison-set", workspace_id, indicator_id, name.casefold()))
        existing = self.connection.execute("SELECT * FROM analysis_comparison_sets WHERE comparison_set_id=?", (entity_id,)).fetchone()
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and int(expected_revision) != actual: self._analysis_concurrency("comparison_set", entity_id, int(expected_revision), actual)
            revision, created_at = actual + 1, existing["created_at"]
        else:
            if expected_revision not in (None, 0): self._analysis_concurrency("comparison_set", entity_id, int(expected_revision), 0)
            revision, created_at = 1, str(comparison_set.get("created_at") or utc_now())
        now = utc_now()
        with self._analysis_transaction():
            self.connection.execute(
                """INSERT INTO analysis_comparison_sets(comparison_set_id,workspace_id,name,description,indicator_id,
                   indicator_definition_id,comparison_policy_json,lifecycle_status,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(comparison_set_id) DO UPDATE SET name=excluded.name,description=excluded.description,
                   indicator_id=excluded.indicator_id,indicator_definition_id=excluded.indicator_definition_id,
                   comparison_policy_json=excluded.comparison_policy_json,lifecycle_status=excluded.lifecycle_status,
                   revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (entity_id, workspace_id, name, str(comparison_set.get("description") or ""), indicator_id,
                 comparison_set.get("indicator_definition_id"), canonical_json(policy),
                 str(comparison_set.get("lifecycle_status") or "draft"), revision, created_at, now,
                 canonical_json(comparison_set.get("metadata") or {})),
            )
            self._audit("create_comparison_set", "analysis_comparison_set", entity_id, workspace_id=workspace_id,
                        revision=revision, actor=actor)
        return self.get_comparison_set(entity_id)

    def get_comparison_set(self, comparison_set_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM analysis_comparison_sets WHERE comparison_set_id=?", (comparison_set_id,)).fetchone()
        if not row: raise AnalysisError(f"comparison set not found: {comparison_set_id}")
        item = self._analysis_decode(row, "comparison_policy_json", "metadata_json")
        rows = self.connection.execute("SELECT * FROM analysis_comparison_members WHERE comparison_set_id=? ORDER BY label,comparison_member_id", (comparison_set_id,)).fetchall()
        item["members"] = [self._analysis_decode(row, "metadata_json") for row in rows]
        return item

    def add_comparison_member(self, comparison_set_id: str, member: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        comparison_set = self.get_comparison_set(comparison_set_id)
        label = str(member.get("label") or "").strip()
        if not label: raise AnalysisError("comparison member label is required")
        if not member.get("initiative_id") and not member.get("benchmark_id") and member.get("value_override") is None:
            raise AnalysisError("comparison member requires initiative_id, benchmark_id, or value_override")
        entity_id = str(member.get("comparison_member_id") or member.get("id") or analysis_id(
            "comparison-member", comparison_set_id, label.casefold(), member.get("initiative_id") or "", member.get("benchmark_id") or ""
        ))
        value_override = finite(member.get("value_override"), "value_override", allow_none=True)
        with self._analysis_transaction():
            self.connection.execute(
                """INSERT INTO analysis_comparison_members(comparison_member_id,comparison_set_id,initiative_id,benchmark_id,
                   label,geography,population,period_label,value_override,unit_id,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(comparison_member_id) DO UPDATE SET initiative_id=excluded.initiative_id,
                   benchmark_id=excluded.benchmark_id,label=excluded.label,geography=excluded.geography,
                   population=excluded.population,period_label=excluded.period_label,value_override=excluded.value_override,
                   unit_id=excluded.unit_id,metadata_json=excluded.metadata_json""",
                (entity_id, comparison_set_id, member.get("initiative_id"), member.get("benchmark_id"), label,
                 str(member.get("geography") or ""), str(member.get("population") or ""),
                 str(member.get("period_label") or ""), value_override, member.get("unit_id"),
                 canonical_json(member.get("metadata") or {})),
            )
            self._audit("add_comparison_member", "analysis_comparison_member", entity_id,
                        workspace_id=comparison_set["workspace_id"], initiative_id=member.get("initiative_id"), actor=actor)
        row = self.connection.execute("SELECT * FROM analysis_comparison_members WHERE comparison_member_id=?", (entity_id,)).fetchone()
        return self._analysis_decode(row, "metadata_json")

    def run_comparison_set(self, comparison_set_id: str, *, actor: str = "system", persist: bool = False) -> Dict[str, Any]:
        comparison_set = self.get_comparison_set(comparison_set_id)
        policy = comparison_set["comparison_policy"]
        candidates: List[Dict[str, Any]] = []
        excluded: List[Dict[str, Any]] = []
        warnings: List[str] = []
        for member in comparison_set["members"]:
            value, unit_id, period_label = member.get("value_override"), member.get("unit_id"), member.get("period_label") or ""
            geography, population = member.get("geography") or "", member.get("population") or ""
            if member.get("benchmark_id"):
                benchmark = self.get_benchmark(member["benchmark_id"])
                value, unit_id = benchmark["value"], benchmark["unit_id"]
                period_label = period_label or benchmark.get("period_label") or ""
                geography = geography or benchmark.get("geography") or ""
                population = population or benchmark.get("population") or ""
            elif member.get("initiative_id") and value is None:
                benchmark_context = {"period_label": period_label} if period_label else None
                observation = self._choose_observation(member["initiative_id"], comparison_set["indicator_id"], benchmark=benchmark_context,
                                                       period_policy=policy["period_policy"] if benchmark_context else "ignore")
                if observation:
                    value, unit_id = observation["value"], observation["unit_id"]
                    period_label = period_label or observation.get("period_label") or ""
                    dimensions = observation.get("dimensions") or {}
                    geography = geography or str(dimensions.get("geography") or "")
                    population = population or str(dimensions.get("population_group") or "")
            if value is None:
                excluded.append({"comparison_member_id": member["comparison_member_id"], "label": member["label"], "reason": "missing_value"})
                continue
            candidates.append({"comparison_member_id": member["comparison_member_id"], "label": member["label"],
                               "value": float(value), "unit_id": unit_id, "period_label": period_label,
                               "geography": geography, "population": population})
        target_unit = next((item["unit_id"] for item in candidates if item.get("unit_id")), None)
        normalized: List[Dict[str, Any]] = []
        for item in candidates:
            try:
                if target_unit and item["unit_id"] != target_unit:
                    item["value"] = self.convert_value(item["value"], item["unit_id"], target_unit,
                                                       workspace_id=comparison_set["workspace_id"])
                    item["unit_id"] = target_unit
                normalized.append(item)
            except Exception as exc:
                excluded.append({"comparison_member_id": item["comparison_member_id"], "label": item["label"],
                                 "reason": "incompatible_unit", "detail": str(exc)})
        if len(normalized) > 1:
            reference = normalized[0]
            for item in normalized[1:]:
                for field, policy_key in (("geography", "geography_policy"), ("population", "population_policy")):
                    if reference[field] and item[field] and reference[field] != item[field]:
                        message = f"{field} differs for {item['label']}: {item[field]!r} versus {reference[field]!r}"
                        if policy[policy_key] == "exact":
                            excluded.append({"comparison_member_id": item["comparison_member_id"], "label": item["label"],
                                             "reason": f"{field}_mismatch"})
                        elif policy[policy_key] == "warn": warnings.append(message)
        excluded_ids = {item["comparison_member_id"] for item in excluded}
        normalized = [item for item in normalized if item["comparison_member_id"] not in excluded_ids]
        reverse = policy["direction"] != "lower_is_better"
        normalized.sort(key=lambda item: (item["value"], item["label"]), reverse=reverse)
        for index, item in enumerate(normalized, 1): item["rank"] = index; item["value"] = _round(item["value"])
        result = {
            "analysis_type": "comparison_set", "analysis_version": ANALYSIS_VERSION,
            "workspace_id": comparison_set["workspace_id"], "comparison_set_id": comparison_set_id,
            "indicator_id": comparison_set["indicator_id"], "policy": policy, "members": normalized,
            "excluded": excluded, "integrity": {"valid": len(normalized) >= 1, "included_count": len(normalized),
                                                 "excluded_count": len(excluded), "warnings": warnings,
                                                 "blockers": [] if normalized else ["no comparable members remain"]},
            "boundary": "Ranking applies only to the declared comparison policy and does not establish causal superiority.",
        }
        if persist:
            return self._record_analysis_run("comparison_set", comparison_set_id, result,
                                             workspace_id=comparison_set["workspace_id"], input_document=policy, actor=actor)
        return result

    def register_uncertainty_model(self, model: Dict[str, Any], *, workspace_id: str,
                                   expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        name = str(model.get("name") or "").strip()
        uncertainty_type = str(model.get("uncertainty_type") or "relative")
        if not name: raise AnalysisError("uncertainty model name is required")
        if uncertainty_type not in UNCERTAINTY_TYPES: raise AnalysisError(f"unsupported uncertainty type: {uncertainty_type}")
        confidence = finite(model.get("confidence_level", 0.95), "confidence_level")
        if confidence is None or not 0 < confidence <= 1: raise AnalysisError("confidence_level must be greater than zero and at most one")
        absolute = finite(model.get("absolute_margin"), "absolute_margin", allow_none=True)
        relative = finite(model.get("relative_margin_percent"), "relative_margin_percent", allow_none=True)
        lower = finite(model.get("lower_bound"), "lower_bound", allow_none=True)
        upper = finite(model.get("upper_bound"), "upper_bound", allow_none=True)
        if absolute is not None and absolute < 0 or relative is not None and relative < 0: raise AnalysisError("uncertainty margins cannot be negative")
        if uncertainty_type == "absolute" and absolute is None: raise AnalysisError("absolute uncertainty requires absolute_margin")
        if uncertainty_type == "relative" and relative is None: raise AnalysisError("relative uncertainty requires relative_margin_percent")
        if uncertainty_type == "bounds" and (lower is None or upper is None or lower > upper): raise AnalysisError("bounds uncertainty requires ordered lower_bound and upper_bound")
        if uncertainty_type == "combined" and absolute is None and relative is None: raise AnalysisError("combined uncertainty requires at least one margin")
        distribution = str(model.get("distribution") or "bounded")
        if distribution not in DISTRIBUTIONS: raise AnalysisError(f"unsupported uncertainty distribution: {distribution}")
        lifecycle = str(model.get("lifecycle_status") or "draft")
        if lifecycle not in LIFECYCLE_STATUSES: raise AnalysisError(f"unsupported lifecycle status: {lifecycle}")
        entity_id = str(model.get("uncertainty_model_id") or model.get("id") or analysis_id("uncertainty-model", workspace_id, name.casefold(), uncertainty_type))
        existing = self.connection.execute("SELECT * FROM analysis_uncertainty_models WHERE uncertainty_model_id=?", (entity_id,)).fetchone()
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and int(expected_revision) != actual: self._analysis_concurrency("uncertainty_model", entity_id, int(expected_revision), actual)
            revision, created_at = actual + 1, existing["created_at"]
        else:
            if expected_revision not in (None, 0): self._analysis_concurrency("uncertainty_model", entity_id, int(expected_revision), 0)
            revision, created_at = 1, str(model.get("created_at") or utc_now())
        now = utc_now()
        with self._analysis_transaction():
            self.connection.execute(
                """INSERT INTO analysis_uncertainty_models(uncertainty_model_id,workspace_id,name,uncertainty_type,
                   confidence_level,absolute_margin,relative_margin_percent,lower_bound,upper_bound,distribution,
                   assumptions_json,limitations_json,source_id,method_definition_id,lifecycle_status,revision,
                   created_at,updated_at,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(uncertainty_model_id) DO UPDATE SET name=excluded.name,uncertainty_type=excluded.uncertainty_type,
                   confidence_level=excluded.confidence_level,absolute_margin=excluded.absolute_margin,
                   relative_margin_percent=excluded.relative_margin_percent,lower_bound=excluded.lower_bound,
                   upper_bound=excluded.upper_bound,distribution=excluded.distribution,assumptions_json=excluded.assumptions_json,
                   limitations_json=excluded.limitations_json,source_id=excluded.source_id,
                   method_definition_id=excluded.method_definition_id,lifecycle_status=excluded.lifecycle_status,
                   revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (entity_id, workspace_id, name, uncertainty_type, confidence, absolute, relative, lower, upper,
                 distribution, canonical_json(list(model.get("assumptions") or [])),
                 canonical_json(list(model.get("limitations") or [])), model.get("source_id"),
                 model.get("method_definition_id"), lifecycle, revision, created_at, now,
                 canonical_json(model.get("metadata") or {})),
            )
            self._audit("register_uncertainty_model", "analysis_uncertainty_model", entity_id,
                        workspace_id=workspace_id, revision=revision, actor=actor)
        return self.get_uncertainty_model(entity_id)

    def get_uncertainty_model(self, uncertainty_model_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM analysis_uncertainty_models WHERE uncertainty_model_id=?", (uncertainty_model_id,)).fetchone()
        if not row: raise AnalysisError(f"uncertainty model not found: {uncertainty_model_id}")
        return self._analysis_decode(row, "assumptions_json", "limitations_json", "metadata_json")

    def list_uncertainty_models(self, workspace_id: str) -> List[Dict[str, Any]]:
        rows = self.connection.execute("SELECT * FROM analysis_uncertainty_models WHERE workspace_id=? ORDER BY name", (workspace_id,)).fetchall()
        return [self._analysis_decode(row, "assumptions_json", "limitations_json", "metadata_json") for row in rows]

    def apply_uncertainty(self, uncertainty_model_id: str, value: float) -> Dict[str, Any]:
        model = self.get_uncertainty_model(uncertainty_model_id)
        center = finite(value, "value") or 0.0
        if model["uncertainty_type"] == "absolute": margin = float(model["absolute_margin"])
        elif model["uncertainty_type"] == "relative": margin = abs(center) * float(model["relative_margin_percent"]) / 100
        elif model["uncertainty_type"] == "bounds":
            return {"uncertainty_model_id": uncertainty_model_id, "value": _round(center),
                    "lower": _round(model["lower_bound"]), "upper": _round(model["upper_bound"]),
                    "margin": None, "confidence_level": model["confidence_level"],
                    "distribution": model["distribution"], "uncertainty_type": model["uncertainty_type"]}
        else:
            absolute = float(model["absolute_margin"] or 0)
            relative = abs(center) * float(model["relative_margin_percent"] or 0) / 100
            margin = math.sqrt(absolute ** 2 + relative ** 2)
        return {"uncertainty_model_id": uncertainty_model_id, "value": _round(center),
                "lower": _round(center - margin), "upper": _round(center + margin), "margin": _round(margin),
                "confidence_level": model["confidence_level"], "distribution": model["distribution"],
                "uncertainty_type": model["uncertainty_type"]}

    def register_scenario(self, scenario: Dict[str, Any], *, workspace_id: str, initiative_id: str,
                          expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        name = str(scenario.get("name") or "").strip()
        indicator_id = str(scenario.get("indicator_id") or "").strip()
        model_type = str(scenario.get("model_type") or "linear")
        scenario_type = str(scenario.get("scenario_type") or "projection")
        if not name or not indicator_id: raise AnalysisError("scenario name and indicator_id are required")
        if model_type not in SCENARIO_MODELS: raise AnalysisError(f"unsupported scenario model: {model_type}")
        if scenario_type not in SCENARIO_TYPES: raise AnalysisError(f"unsupported scenario type: {scenario_type}")
        periods = int(scenario.get("periods") or 1)
        if periods < 1: raise AnalysisError("scenario periods must be at least one")
        base_value = finite(scenario.get("base_value"), "base_value", allow_none=True)
        unit = self.get_unit(str(scenario.get("unit_id") or scenario.get("unit") or "count"), workspace_id=workspace_id)
        parameters = dict(scenario.get("parameters") or {})
        for key in ("period_change", "annual_change", "growth_rate_percent", "step_value", "step_period", "ceiling", "floor"):
            if key in parameters and parameters[key] not in (None, ""): parameters[key] = finite(parameters[key], key)
        entity_id = str(scenario.get("scenario_id") or scenario.get("id") or analysis_id("scenario", workspace_id, initiative_id, indicator_id, name.casefold()))
        existing = self.connection.execute("SELECT * FROM analysis_scenarios WHERE scenario_id=?", (entity_id,)).fetchone()
        if existing:
            actual = int(existing["revision"])
            if expected_revision is not None and int(expected_revision) != actual: self._analysis_concurrency("scenario", entity_id, int(expected_revision), actual)
            revision, created_at = actual + 1, existing["created_at"]
        else:
            if expected_revision not in (None, 0): self._analysis_concurrency("scenario", entity_id, int(expected_revision), 0)
            revision, created_at = 1, str(scenario.get("created_at") or utc_now())
        now = utc_now()
        with self._analysis_transaction():
            self.connection.execute(
                """INSERT INTO analysis_scenarios(scenario_id,workspace_id,initiative_id,indicator_id,
                   indicator_definition_id,name,description,scenario_type,model_type,unit_id,start_period,end_period,
                   periods,base_value,parameters_json,assumptions_json,limitations_json,source_id,
                   method_definition_id,target_model_id,lifecycle_status,revision,created_at,updated_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(scenario_id) DO UPDATE SET indicator_id=excluded.indicator_id,
                   indicator_definition_id=excluded.indicator_definition_id,name=excluded.name,description=excluded.description,
                   scenario_type=excluded.scenario_type,model_type=excluded.model_type,unit_id=excluded.unit_id,
                   start_period=excluded.start_period,end_period=excluded.end_period,periods=excluded.periods,
                   base_value=excluded.base_value,parameters_json=excluded.parameters_json,
                   assumptions_json=excluded.assumptions_json,limitations_json=excluded.limitations_json,
                   source_id=excluded.source_id,method_definition_id=excluded.method_definition_id,
                   target_model_id=excluded.target_model_id,lifecycle_status=excluded.lifecycle_status,
                   revision=excluded.revision,updated_at=excluded.updated_at,metadata_json=excluded.metadata_json""",
                (entity_id, workspace_id, initiative_id, indicator_id, scenario.get("indicator_definition_id"), name,
                 str(scenario.get("description") or ""), scenario_type, model_type, unit["unit_id"],
                 str(scenario.get("start_period") or ""), str(scenario.get("end_period") or ""), periods, base_value,
                 canonical_json(parameters), canonical_json(list(scenario.get("assumptions") or [])),
                 canonical_json(list(scenario.get("limitations") or [])), scenario.get("source_id"),
                 scenario.get("method_definition_id"), scenario.get("target_model_id"),
                 str(scenario.get("lifecycle_status") or "draft"), revision, created_at, now,
                 canonical_json(scenario.get("metadata") or {})),
            )
            self._audit("register_scenario", "analysis_scenario", entity_id, workspace_id=workspace_id,
                        initiative_id=initiative_id, revision=revision, actor=actor)
        return self.get_scenario(entity_id)

    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM analysis_scenarios WHERE scenario_id=?", (scenario_id,)).fetchone()
        if not row: raise AnalysisError(f"scenario not found: {scenario_id}")
        return self._analysis_decode(row, "parameters_json", "assumptions_json", "limitations_json", "metadata_json")

    def list_scenarios(self, *, workspace_id: Optional[str] = None, initiative_id: Optional[str] = None) -> List[Dict[str, Any]]:
        clauses, params = ["1=1"], []
        for field, value in (("workspace_id", workspace_id), ("initiative_id", initiative_id)):
            if value is not None: clauses.append(f"{field}=?"); params.append(value)
        rows = self.connection.execute(f"SELECT * FROM analysis_scenarios WHERE {' AND '.join(clauses)} ORDER BY name,scenario_id", params).fetchall()
        return [self._analysis_decode(row, "parameters_json", "assumptions_json", "limitations_json", "metadata_json") for row in rows]

    def _scenario_base_value(self, scenario: Dict[str, Any]) -> Tuple[float, Optional[str]]:
        if scenario.get("base_value") is not None: return float(scenario["base_value"]), None
        observations = self._effective_records(self.list_observations(initiative_id=scenario["initiative_id"], indicator_id=scenario["indicator_id"]), "observation_record_id")
        observations = [item for item in observations if item["data_state"] != "missing" and item.get("value") is not None]
        observations.sort(key=lambda item: (item.get("period_start") or item.get("period_label") or "", item.get("received_at") or ""))
        if not observations: raise ScenarioEvaluationError("scenario has no explicit base value or usable observation")
        latest = observations[-1]
        value = float(latest["value"])
        if latest["unit_id"] != scenario["unit_id"]:
            value = self.convert_value(value, latest["unit_id"], scenario["unit_id"], workspace_id=scenario["workspace_id"])
        return value, latest["observation_record_id"]

    @staticmethod
    def _scenario_value(model_type: str, base: float, period_index: int, parameters: Dict[str, Any]) -> float:
        if model_type == "constant": value = base
        elif model_type == "linear": value = base + float(parameters.get("period_change", parameters.get("annual_change", 0))) * period_index
        elif model_type == "compound": value = base * ((1 + float(parameters.get("growth_rate_percent", 0)) / 100) ** period_index)
        elif model_type == "step": value = float(parameters.get("step_value", base)) if period_index >= int(parameters.get("step_period", 1)) else base
        else: raise ScenarioEvaluationError(f"unsupported scenario model: {model_type}")
        if parameters.get("ceiling") is not None: value = min(value, float(parameters["ceiling"]))
        if parameters.get("floor") is not None: value = max(value, float(parameters["floor"]))
        return value

    def evaluate_scenario(self, scenario_id: str, *, parameter_overrides: Optional[Dict[str, Any]] = None,
                          uncertainty_model_id: Optional[str] = None, actor: str = "system",
                          persist: bool = True) -> Dict[str, Any]:
        scenario = self.get_scenario(scenario_id)
        parameters = dict(scenario["parameters"])
        parameters.update(dict(parameter_overrides or {}))
        for key, value in list(parameters.items()):
            if isinstance(value, (int, float, str)) and key in {"period_change", "annual_change", "growth_rate_percent", "step_value", "step_period", "ceiling", "floor"}:
                parameters[key] = finite(value, key)
        base, base_observation_id = self._scenario_base_value(scenario)
        points: List[Dict[str, Any]] = []
        for index in range(int(scenario["periods"]) + 1):
            value = self._scenario_value(scenario["model_type"], base, index, parameters)
            point: Dict[str, Any] = {"period_index": index, "value": _round(value), "unit_id": scenario["unit_id"]}
            if uncertainty_model_id: point["uncertainty"] = self.apply_uncertainty(uncertainty_model_id, value)
            if scenario.get("target_model_id"):
                target = self.evaluate_target(scenario["target_model_id"], baseline_value=base,
                                              progress_fraction=index / max(1, int(scenario["periods"])))
                target_value = target.get("value")
                if target_value is not None:
                    if target["unit_id"] != scenario["unit_id"]:
                        target_value = self.convert_value(target_value, target["unit_id"], scenario["unit_id"], workspace_id=scenario["workspace_id"])
                    point["target_value"] = _round(target_value)
                    point["target_gap"] = _round(value - target_value)
            points.append(point)
        result = {
            "analysis_type": "scenario_evaluation", "analysis_version": ANALYSIS_VERSION,
            "workspace_id": scenario["workspace_id"], "initiative_id": scenario["initiative_id"],
            "scenario_id": scenario_id, "indicator_id": scenario["indicator_id"], "model_type": scenario["model_type"],
            "unit_id": scenario["unit_id"], "base_value": _round(base), "base_observation_id": base_observation_id,
            "parameters": parameters, "points": points, "assumptions": scenario["assumptions"],
            "limitations": scenario["limitations"], "uncertainty_model_id": uncertainty_model_id,
            "integrity": {"valid": True, "point_count": len(points), "warnings": []},
            "boundary": "Scenario output is a conditional planning calculation, not a forecast or causal estimate.",
        }
        if persist:
            return self._record_analysis_run("scenario_evaluation", scenario_id, result,
                                             workspace_id=scenario["workspace_id"], initiative_id=scenario["initiative_id"],
                                             input_document={"parameter_overrides": parameter_overrides or {},
                                                             "uncertainty_model_id": uncertainty_model_id}, actor=actor)
        return result

    def run_sensitivity_analysis(self, scenario_id: str, parameter_ranges: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        scenario = self.get_scenario(scenario_id)
        base_parameters = dict(scenario["parameters"])
        base_value, _ = self._scenario_base_value(scenario)
        periods = int(scenario["periods"])
        results: List[Dict[str, Any]] = []
        for parameter, limits in parameter_ranges.items():
            if not isinstance(limits, (list, tuple)) or len(limits) != 2: raise AnalysisError(f"sensitivity range for {parameter} must contain [low, high]")
            low, high = finite(limits[0], f"{parameter} low"), finite(limits[1], f"{parameter} high")
            baseline = finite(base_parameters.get(parameter, 0), f"{parameter} baseline") or 0.0
            low_parameters, baseline_parameters, high_parameters = dict(base_parameters), dict(base_parameters), dict(base_parameters)
            low_parameters[parameter], baseline_parameters[parameter], high_parameters[parameter] = low, baseline, high
            low_result = self._scenario_value(scenario["model_type"], base_value, periods, low_parameters)
            baseline_result = self._scenario_value(scenario["model_type"], base_value, periods, baseline_parameters)
            high_result = self._scenario_value(scenario["model_type"], base_value, periods, high_parameters)
            effect = abs(high_result - low_result)
            results.append({"parameter_name": parameter, "baseline_value": _round(baseline), "low_value": _round(low),
                            "high_value": _round(high), "low_result": _round(low_result),
                            "baseline_result": _round(baseline_result), "high_result": _round(high_result),
                            "absolute_effect": _round(effect),
                            "relative_effect_percent": None if baseline_result == 0 else _round(effect / abs(baseline_result) * 100)})
        results.sort(key=lambda item: (-float(item["absolute_effect"]), item["parameter_name"]))
        now = utc_now()
        with self._analysis_transaction():
            for rank, item in enumerate(results, 1):
                item["rank"] = rank
                sensitivity_id = analysis_id("sensitivity", scenario_id, item["parameter_name"], item["low_value"], item["high_value"])
                item["sensitivity_run_id"] = sensitivity_id
                self.connection.execute(
                    """INSERT OR REPLACE INTO analysis_sensitivity_runs(sensitivity_run_id,scenario_id,workspace_id,
                       initiative_id,parameter_name,baseline_value,low_value,high_value,low_result,baseline_result,
                       high_result,absolute_effect,relative_effect_percent,rank_order,created_by,created_at,metadata_json)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (sensitivity_id, scenario_id, scenario["workspace_id"], scenario["initiative_id"], item["parameter_name"],
                     item["baseline_value"], item["low_value"], item["high_value"], item["low_result"],
                     item["baseline_result"], item["high_result"], item["absolute_effect"], item["relative_effect_percent"],
                     rank, actor, now, canonical_json({})),
                )
        result = {"analysis_type": "sensitivity", "analysis_version": ANALYSIS_VERSION,
                  "workspace_id": scenario["workspace_id"], "initiative_id": scenario["initiative_id"],
                  "scenario_id": scenario_id, "parameters": results,
                  "integrity": {"valid": bool(results), "parameter_count": len(results), "warnings": []},
                  "boundary": "Sensitivity measures model responsiveness and does not rank real-world causal importance."}
        return self._record_analysis_run("sensitivity", scenario_id, result, workspace_id=scenario["workspace_id"],
                                         initiative_id=scenario["initiative_id"], input_document=parameter_ranges, actor=actor)

    def compare_observations_to_target(self, initiative_id: str, indicator_id: str, target_model_id: str, *,
                                       actor: str = "system", persist: bool = False) -> Dict[str, Any]:
        records = self._effective_records(self.list_observations(initiative_id=initiative_id, indicator_id=indicator_id), "observation_record_id")
        records = [item for item in records if item["data_state"] != "missing" and item.get("value") is not None]
        records.sort(key=lambda item: (item.get("period_start") or item.get("period_label") or "", item.get("received_at") or ""))
        target_model = self.get_target_model(target_model_id)
        contract = self.get_contract(initiative_id=initiative_id)
        baseline = records[0]["value"] if records else None
        points: List[Dict[str, Any]] = []
        for index, observation in enumerate(records):
            fraction = index / max(1, len(records) - 1)
            target = self.evaluate_target(target_model_id, baseline_value=baseline, progress_fraction=fraction,
                                          period_label=observation["period_label"] if target_model["target_type"] == "trajectory" and target_model.get("milestones") else None)
            target_value = target.get("value")
            observation_value = float(observation["value"])
            if observation["unit_id"] != target["unit_id"]:
                observation_value = self.convert_value(observation_value, observation["unit_id"], target["unit_id"], workspace_id=contract["workspace_id"])
            points.append({"observation_record_id": observation["observation_record_id"],
                           "period_label": observation["period_label"], "observed_value": _round(observation_value),
                           "target_value": _round(target_value), "gap": _round(observation_value - float(target_value)),
                           "unit_id": target["unit_id"], "progress_fraction": _round(fraction)})
        result = {"analysis_type": "target_trajectory", "analysis_version": ANALYSIS_VERSION,
                  "workspace_id": contract["workspace_id"], "initiative_id": initiative_id,
                  "indicator_id": indicator_id, "target_model_id": target_model_id, "points": points,
                  "integrity": {"valid": bool(points), "point_count": len(points),
                                "warnings": [] if points else ["no usable observations"]},
                  "boundary": "Target gaps compare governed records but do not prove achievability or attribution."}
        if persist:
            return self._record_analysis_run("target_trajectory", target_model_id, result,
                                             workspace_id=contract["workspace_id"], initiative_id=initiative_id,
                                             input_document={"indicator_id": indicator_id}, actor=actor)
        return result

    def export_analysis_repository(self, workspace_id: str) -> Dict[str, Any]:
        benchmarks = self.list_benchmarks(workspace_id=workspace_id)
        comparison_sets = [self.get_comparison_set(row["comparison_set_id"]) for row in self.connection.execute(
            "SELECT comparison_set_id FROM analysis_comparison_sets WHERE workspace_id=? ORDER BY name", (workspace_id,)).fetchall()]
        scenarios = self.list_scenarios(workspace_id=workspace_id)
        uncertainty = self.list_uncertainty_models(workspace_id)
        runs = self.list_analysis_runs(workspace_id=workspace_id)
        sensitivity = [self._analysis_decode(row, "metadata_json") for row in self.connection.execute(
            "SELECT * FROM analysis_sensitivity_runs WHERE workspace_id=? ORDER BY scenario_id,rank_order", (workspace_id,)).fetchall()]
        benchmark_ids = {item["benchmark_id"] for item in benchmarks}
        scenario_ids = {item["scenario_id"] for item in scenarios}
        orphan_members = [member["comparison_member_id"] for item in comparison_sets for member in item["members"]
                          if member.get("benchmark_id") and member["benchmark_id"] not in benchmark_ids]
        orphan_sensitivity = [item["sensitivity_run_id"] for item in sensitivity if item["scenario_id"] not in scenario_ids]
        return {"repository_type": "global_impact_analysis_repository", "repository_version": ANALYSIS_VERSION,
                "workspace_id": workspace_id, "generated_at": utc_now(), "benchmarks": benchmarks,
                "comparison_sets": comparison_sets, "scenarios": scenarios, "uncertainty_models": uncertainty,
                "analysis_runs": runs, "sensitivity_runs": sensitivity,
                "integrity": {"valid": not orphan_members and not orphan_sensitivity,
                              "benchmark_count": len(benchmarks), "comparison_set_count": len(comparison_sets),
                              "comparison_member_count": sum(len(item["members"]) for item in comparison_sets),
                              "scenario_count": len(scenarios), "uncertainty_model_count": len(uncertainty),
                              "analysis_run_count": len(runs), "sensitivity_run_count": len(sensitivity),
                              "orphan_comparison_member_ids": orphan_members,
                              "orphan_sensitivity_run_ids": orphan_sensitivity},
                "boundary": "Analysis records improve transparency but do not create assurance, certification, causality, or verified forecasts."}

    def _restore_analysis_repository(self, repository: Dict[str, Any], *, actor: str = "restore") -> None:
        if not repository: return
        workspace_id = repository["workspace_id"]
        for benchmark in repository.get("benchmarks", []):
            self.register_benchmark(benchmark, workspace_id=workspace_id, actor=actor)
        for comparison_set in repository.get("comparison_sets", []):
            record = dict(comparison_set); members = record.pop("members", [])
            self.create_comparison_set(record, workspace_id=workspace_id, actor=actor)
            for member in members: self.add_comparison_member(comparison_set["comparison_set_id"], member, actor=actor)
        for model in repository.get("uncertainty_models", []):
            self.register_uncertainty_model(model, workspace_id=workspace_id, actor=actor)
        for scenario in repository.get("scenarios", []):
            self.register_scenario(scenario, workspace_id=workspace_id, initiative_id=scenario["initiative_id"], actor=actor)
        for run in repository.get("analysis_runs", []):
            result = run.get("result") or {}
            self.connection.execute(
                """INSERT OR REPLACE INTO analysis_runs(analysis_run_id,workspace_id,initiative_id,analysis_type,
                   subject_id,input_hash,result_hash,result_json,created_by,created_at,metadata_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (run["analysis_run_id"], run["workspace_id"], run.get("initiative_id"), run["analysis_type"],
                 run["subject_id"], run["input_hash"], run["result_hash"], canonical_json(result),
                 run["created_by"], run["created_at"], canonical_json(run.get("metadata") or {})),
            )
        for item in repository.get("sensitivity_runs", []):
            columns = ["sensitivity_run_id","scenario_id","workspace_id","initiative_id","parameter_name",
                       "baseline_value","low_value","high_value","low_result","baseline_result","high_result",
                       "absolute_effect","relative_effect_percent","rank_order","created_by","created_at"]
            self.connection.execute(
                f"INSERT OR REPLACE INTO analysis_sensitivity_runs({','.join(columns)},metadata_json) VALUES ({','.join('?' for _ in range(len(columns)+1))})",
                [item.get(column) for column in columns] + [canonical_json(item.get("metadata") or {})],
            )
