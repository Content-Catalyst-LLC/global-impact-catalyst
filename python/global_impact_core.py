"""Canonical Global Impact Catalyst v1.1.0 contract and validation engine.

The authoring input remains compact, but the durable output is a versioned,
entity-oriented impact contract. Entered facts are separated from derived
metrics and interpretations. Every material entity has a stable identifier and
timestamps. Validation produces structured, actionable issues rather than
opaque strings.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

ENGINE_VERSION = "1.1.0"
CONTRACT_VERSION = "1.1.0"
SCHEMA_VERSION = "1.1.0"
CONTRACT_TYPE = "global_impact_contract"
LEGACY_RECORD_TYPES = {"global_impact_catalyst_record"}
CONFIDENCE_VALUES = {"low", "medium", "high"}
REVIEW_STATUS_VALUES = {"draft", "needs_review", "reviewed", "published"}
CLAIM_TYPES = {
    "descriptive_observation",
    "progress_to_target_statement",
    "comparison",
    "contribution_statement",
    "causal_claim",
}
DESIGN_TYPES = {
    "monitoring",
    "before_after",
    "comparison_group",
    "quasi_experimental",
    "randomized",
    "qualitative",
    "mixed_methods",
}
SEVERITIES = {"error", "warning", "info"}
TRACEABILITY_PATH = [
    "workspace",
    "initiative",
    "goal",
    "outcome",
    "indicator definition",
    "baseline",
    "observation",
    "target",
    "source",
    "method",
    "interpretation",
    "claim",
    "review",
    "revision",
    "publication",
]
BOUNDARIES = [
    "This contract is not an ESG assurance opinion, SDG certification, regulatory filing, or audit finding.",
    "Derived progress does not establish causality, contribution, attribution, or comparative superiority.",
    "Claims depend on documented sources, method design, indicator definition, and human review.",
    "Validation checks contract consistency; it does not automatically verify truth or source authenticity.",
]


class InputValidationError(ValueError):
    """Raised when an input value cannot be normalized."""


class ContractValidationError(ValueError):
    """Raised in strict mode when a contract contains validation errors."""

    def __init__(self, issues: Sequence[Dict[str, Any]]):
        self.issues = list(issues)
        super().__init__("impact contract validation failed")


@dataclass(frozen=True)
class GlobalImpactInput:
    workspace: str
    initiative: str
    goal: str
    outcome: str
    sdg_theme: str
    indicator: str
    indicator_definition: str
    unit: str
    baseline_unit: str
    current_unit: str
    target_unit: str
    baseline_value: float
    current_value: float
    target_value: float
    baseline_period: str
    current_period: str
    target_period: str
    source: str
    source_locator: str
    method_name: str
    method_notes: str
    method_version: str
    design_type: str
    confidence: str
    review_status: str
    beneficiaries: Optional[int]
    population_group: str
    geography: str
    budget_usd: Optional[float]
    budget_currency: str
    higher_is_better: bool
    claim_type: str
    claim_statement: str
    comparison_basis: str
    contribution_rationale: str
    causal_design: str
    record_id: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ValidationIssue:
    issue_id: str
    severity: str
    path: str
    rule_id: str
    message: str
    remediation: str


# ---------- normalization ----------

def _round(value: float, places: int) -> float:
    quantum = Decimal("1").scaleb(-places)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def _text(data: Dict[str, Any], key: str, default: str = "") -> str:
    value = data.get(key, default)
    return str(default if value is None else value).strip()


def _enum(value: Any, allowed: set[str], default: str) -> str:
    cleaned = str(default if value is None else value).strip().lower().replace(" ", "_").replace("-", "_")
    return cleaned if cleaned in allowed else default


def _parse_boolean(value: Any, *, field: str, default: bool) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in {"true", "1", "yes", "y", "on"}:
            return True
        if cleaned in {"false", "0", "no", "n", "off"}:
            return False
    raise InputValidationError(f"{field} must be a boolean or recognized boolean string")


def _parse_number(value: Any, *, field: str, default: Optional[float] = None) -> float:
    if value is None or (isinstance(value, str) and not value.strip()):
        if default is None:
            raise InputValidationError(f"{field} is required")
        return float(default)
    if isinstance(value, bool):
        raise InputValidationError(f"{field} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise InputValidationError(f"{field} must be a finite number") from exc
    if not math.isfinite(number):
        raise InputValidationError(f"{field} must be a finite number")
    return number


def _parse_optional_number(value: Any, *, field: str, minimum: float = 0.0) -> Optional[float]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    number = _parse_number(value, field=field)
    if number < minimum:
        raise InputValidationError(f"{field} must be greater than or equal to {minimum:g}")
    return number


def _parse_optional_integer(value: Any, *, field: str, minimum: int = 0) -> Optional[int]:
    number = _parse_optional_number(value, field=field, minimum=minimum)
    if number is None:
        return None
    if not number.is_integer():
        raise InputValidationError(f"{field} must be an integer")
    return int(number)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_timestamp(value: str, fallback: str) -> str:
    return value.strip() or fallback


def input_from_dict(data: Dict[str, Any]) -> GlobalImpactInput:
    """Normalize compact authoring input without hiding semantically missing text."""
    if not isinstance(data, dict):
        raise InputValidationError("input must be a JSON object")
    created = _text(data, "created_at")
    updated = _text(data, "updated_at")
    source = _text(data, "source")
    return GlobalImpactInput(
        workspace=_text(data, "workspace", "Default workspace"),
        initiative=_text(data, "initiative"),
        goal=_text(data, "goal"),
        outcome=_text(data, "outcome") or _text(data, "goal"),
        sdg_theme=_text(data, "sdg_theme", "Sustainable development"),
        indicator=_text(data, "indicator"),
        indicator_definition=_text(data, "indicator_definition") or _text(data, "indicator"),
        unit=_text(data, "unit"),
        baseline_unit=_text(data, "baseline_unit") or _text(data, "unit"),
        current_unit=_text(data, "current_unit") or _text(data, "unit"),
        target_unit=_text(data, "target_unit") or _text(data, "unit"),
        baseline_value=_parse_number(data.get("baseline_value"), field="baseline_value", default=0),
        current_value=_parse_number(data.get("current_value"), field="current_value", default=0),
        target_value=_parse_number(data.get("target_value"), field="target_value", default=100),
        baseline_period=_text(data, "baseline_period"),
        current_period=_text(data, "current_period"),
        target_period=_text(data, "target_period") or _text(data, "current_period"),
        source=source,
        source_locator=_text(data, "source_locator") or source,
        method_name=_text(data, "method_name", "Entered measurement method"),
        method_notes=_text(data, "method_notes"),
        method_version=_text(data, "method_version", "1.0"),
        design_type=_enum(data.get("design_type"), DESIGN_TYPES, "before_after"),
        confidence=_enum(data.get("confidence"), CONFIDENCE_VALUES, "medium"),
        review_status=_enum(data.get("review_status"), REVIEW_STATUS_VALUES, "draft"),
        beneficiaries=_parse_optional_integer(data.get("beneficiaries"), field="beneficiaries"),
        population_group=_text(data, "population_group", "Affected population"),
        geography=_text(data, "geography", "Not specified"),
        budget_usd=_parse_optional_number(data.get("budget_usd"), field="budget_usd"),
        budget_currency=_text(data, "budget_currency", "USD").upper(),
        higher_is_better=_parse_boolean(data.get("higher_is_better", True), field="higher_is_better", default=True),
        claim_type=_enum(data.get("claim_type"), CLAIM_TYPES, "progress_to_target_statement"),
        claim_statement=_text(data, "claim_statement"),
        comparison_basis=_text(data, "comparison_basis"),
        contribution_rationale=_text(data, "contribution_rationale"),
        causal_design=_text(data, "causal_design"),
        record_id=_text(data, "record_id"),
        created_at=created,
        updated_at=updated,
    )


# ---------- deterministic identity ----------

def _canonical_number(value: Optional[float | int]) -> str:
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    return format(value, ".15g")


def _seed_material(inp: GlobalImpactInput) -> str:
    values: Iterable[str] = (
        inp.workspace,
        inp.initiative,
        inp.goal,
        inp.outcome,
        inp.sdg_theme,
        inp.indicator,
        inp.indicator_definition,
        inp.unit,
        _canonical_number(inp.baseline_value),
        _canonical_number(inp.current_value),
        _canonical_number(inp.target_value),
        inp.baseline_period,
        inp.current_period,
        inp.target_period,
        inp.source,
        inp.method_notes,
        inp.claim_type,
    )
    return "\x1f".join(values)


def _fnv1a(text: str) -> int:
    value = 0x811C9DC5
    for byte in text.encode("utf-8"):
        value ^= byte
        value = (value * 0x01000193) & 0xFFFFFFFF
    return value


def stable_token(text: str) -> str:
    return f"{_fnv1a(text):08x}{_fnv1a('gic|' + text):08x}"


def stable_id(kind: str, seed: str) -> str:
    return f"gic-{kind}-{stable_token(kind + '|' + seed)}"


def _entity(kind: str, seed: str, timestamp: str, **fields: Any) -> Dict[str, Any]:
    return {
        "entity_type": kind,
        "id": stable_id(kind.replace("_", "-"), seed),
        "created_at": timestamp,
        "updated_at": timestamp,
        **fields,
    }


# ---------- metrics ----------

def _safe_percent(numerator: float, denominator: float) -> Optional[float]:
    return None if denominator == 0 else (numerator / denominator) * 100.0


def _progress(inp: GlobalImpactInput) -> Optional[float]:
    if inp.higher_is_better:
        raw = _safe_percent(inp.current_value - inp.baseline_value, inp.target_value - inp.baseline_value)
    else:
        raw = _safe_percent(inp.baseline_value - inp.current_value, inp.baseline_value - inp.target_value)
    return None if raw is None else _round(raw, 2)


def _status(progress: Optional[float], inp: GlobalImpactInput) -> str:
    if progress is None:
        return "needs baseline/target review"
    prefix = "draft — " if inp.review_status in {"draft", "needs_review"} else "reviewed — "
    if inp.confidence == "low":
        return prefix + "interpret cautiously"
    if progress >= 100:
        return prefix + "target reached or exceeded"
    if progress >= 75:
        return prefix + "near target"
    if progress >= 40:
        return prefix + "partial progress"
    if progress >= 0:
        return prefix + "early progress"
    return prefix + "moving away from target"


def _quality_components(inp: GlobalImpactInput) -> Dict[str, int]:
    return {
        "source_documented": 25 if inp.source else 0,
        "method_documented": 25 if len(inp.method_notes) >= 20 else 0,
        "confidence_signal": {"high": 25, "medium": 15, "low": 5}[inp.confidence],
        "review_signal": 25 if inp.review_status in {"reviewed", "published"} else 10 if inp.review_status == "needs_review" else 0,
    }


def derive_metrics(inp: GlobalImpactInput) -> Dict[str, Any]:
    absolute = inp.current_value - inp.baseline_value
    percent = _safe_percent(absolute, inp.baseline_value)
    progress = _progress(inp)
    gap = inp.target_value - inp.current_value if inp.higher_is_better else inp.current_value - inp.target_value
    cost = None
    if inp.beneficiaries is not None and inp.beneficiaries > 0 and inp.budget_usd is not None:
        cost = _round(inp.budget_usd / inp.beneficiaries, 2)
    components = _quality_components(inp)
    return {
        "absolute_change": _round(absolute, 4),
        "percent_change_from_baseline": None if percent is None else _round(percent, 2),
        "progress_to_target_percent": progress,
        "remaining_gap": _round(gap, 4),
        "status": _status(progress, inp),
        "cost_per_beneficiary": None if cost is None else {"value": cost, "currency": inp.budget_currency},
        "data_quality_score": min(sum(components.values()), 100),
        "data_quality_components": components,
        "calculation_method": {
            "engine": "global-impact-catalyst",
            "engine_version": ENGINE_VERSION,
            "rounding": "decimal half up",
            "progress_formula": "direction-aware change from baseline divided by baseline-to-target distance",
        },
    }


# ---------- validation ----------

def _period_key(label: str) -> Optional[tuple[int, int]]:
    match = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", label)
    if not match:
        return None
    year = int(match.group(1))
    q = re.search(r"\bQ([1-4])\b", label, re.IGNORECASE)
    return year, int(q.group(1)) if q else 0


def _issue(severity: str, path: str, rule: str, message: str, remediation: str) -> ValidationIssue:
    token = stable_token("|".join([severity, path, rule, message]))
    return ValidationIssue(f"gic-issue-{token}", severity, path, rule, message, remediation)


def validate_input(inp: GlobalImpactInput) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    required = {
        "$.facts.initiative.name": inp.initiative,
        "$.facts.goal.statement": inp.goal,
        "$.facts.indicator.name": inp.indicator,
        "$.facts.indicator.definition.unit": inp.unit,
        "$.facts.measurement.baseline.period.label": inp.baseline_period,
        "$.facts.measurement.observations[0].period.label": inp.current_period,
        "$.facts.sources[0].title": inp.source,
        "$.facts.methods[0].description": inp.method_notes,
    }
    for path, value in required.items():
        if not value:
            issues.append(_issue("error", path, "GIC-REQ-001", "Required impact fact is missing.", "Enter a specific value and regenerate the contract."))

    units = [inp.unit, inp.baseline_unit, inp.current_unit, inp.target_unit]
    normalized_units = {unit.strip().casefold() for unit in units if unit.strip()}
    if len(normalized_units) > 1:
        issues.append(_issue("error", "$.facts.measurement", "GIC-UNIT-001", "Baseline, observation, target, and indicator units are not compatible.", "Use one canonical unit or convert all values before calculating progress."))
    if any("\n" in unit or len(unit) > 64 for unit in units):
        issues.append(_issue("error", "$.facts.indicator.definition.unit", "GIC-UNIT-002", "Unit labels must be concise single-line values.", "Use a recognized short unit label such as people, %, kg, kWh, or USD."))

    baseline_key = _period_key(inp.baseline_period)
    current_key = _period_key(inp.current_period)
    if baseline_key and current_key and baseline_key > current_key:
        issues.append(_issue("error", "$.facts.measurement", "GIC-PERIOD-001", "Baseline period occurs after the current observation period.", "Correct the period labels or reverse the measurement roles."))
    elif not baseline_key or not current_key:
        issues.append(_issue("warning", "$.facts.measurement", "GIC-PERIOD-002", "Period ordering could not be verified from the labels.", "Use labels containing an unambiguous four-digit year and optional quarter."))

    if inp.baseline_value == inp.target_value:
        issues.append(_issue("error", "$.facts.measurement.target.value", "GIC-TARGET-001", "Baseline and target values are equal, so progress to target is undefined.", "Choose a target different from the baseline or omit the progress claim."))
    elif inp.higher_is_better and inp.target_value < inp.baseline_value:
        issues.append(_issue("error", "$.facts.measurement.target.value", "GIC-DIRECTION-001", "A higher-is-better indicator has a target below its baseline.", "Change the direction to lower-is-better or correct the target."))
    elif not inp.higher_is_better and inp.target_value > inp.baseline_value:
        issues.append(_issue("error", "$.facts.measurement.target.value", "GIC-DIRECTION-002", "A lower-is-better indicator has a target above its baseline.", "Change the direction to higher-is-better or correct the target."))

    if inp.source and not inp.source_locator:
        issues.append(_issue("warning", "$.facts.sources[0].locator", "GIC-SOURCE-001", "Source is named but has no retrievable locator.", "Add a URL, citation, file identifier, or repository location."))
    if inp.method_notes and len(inp.method_notes) < 20:
        issues.append(_issue("warning", "$.facts.methods[0].description", "GIC-METHOD-001", "Method description is too brief for reproducibility.", "Describe population, collection procedure, calculation, exclusions, and limitations."))

    if inp.claim_type == "comparison":
        if inp.design_type not in {"comparison_group", "quasi_experimental", "randomized", "mixed_methods"}:
            issues.append(_issue("error", "$.derived.claims[0].design_metadata.design_type", "GIC-CLAIM-COMP-001", "Comparison claims require a design with an explicit comparison basis.", "Select comparison_group, quasi_experimental, randomized, or mixed_methods."))
        if not inp.comparison_basis:
            issues.append(_issue("error", "$.derived.claims[0].design_metadata.comparison_basis", "GIC-CLAIM-COMP-002", "Comparison basis is missing.", "Name the comparator, benchmark, counterfactual, or reference group."))
    elif inp.claim_type == "contribution_statement":
        if not inp.contribution_rationale:
            issues.append(_issue("error", "$.derived.claims[0].design_metadata.contribution_rationale", "GIC-CLAIM-CONTRIB-001", "Contribution statement lacks a documented rationale.", "Describe the plausible mechanism, other contributors, and supporting evidence."))
        if inp.design_type == "monitoring":
            issues.append(_issue("warning", "$.derived.claims[0].design_metadata.design_type", "GIC-CLAIM-CONTRIB-002", "Monitoring alone provides limited support for contribution language.", "Use cautious wording or add comparative, qualitative, or theory-based evidence."))
    elif inp.claim_type == "causal_claim":
        if inp.design_type not in {"quasi_experimental", "randomized"}:
            issues.append(_issue("error", "$.derived.claims[0].design_metadata.design_type", "GIC-CLAIM-CAUSAL-001", "Causal claims require a quasi-experimental or randomized design.", "Select an eligible design and document its assumptions, assignment, and analysis."))
        if not inp.causal_design:
            issues.append(_issue("error", "$.derived.claims[0].design_metadata.causal_design", "GIC-CLAIM-CAUSAL-002", "Causal design metadata is missing.", "Document identification strategy, assignment process, controls, threats, and analysis."))
        if inp.confidence != "high":
            issues.append(_issue("error", "$.derived.claims[0].confidence", "GIC-CLAIM-CAUSAL-003", "Causal claims require high declared confidence.", "Downgrade the claim or complete the evidence review needed for high confidence."))
        if inp.review_status not in {"reviewed", "published"}:
            issues.append(_issue("error", "$.governance.reviews[0].status", "GIC-CLAIM-CAUSAL-004", "Causal claims cannot remain draft or needs-review.", "Complete independent review before using causal language."))

    if inp.claim_type in {"comparison", "contribution_statement", "causal_claim"} and not inp.claim_statement:
        issues.append(_issue("error", "$.derived.claims[0].statement", "GIC-CLAIM-001", "Stronger claim types require an explicit claim statement.", "Enter the exact sentence that evidence and review are intended to support."))
    return issues


def validation_result(issues: Sequence[ValidationIssue | Dict[str, Any]]) -> Dict[str, Any]:
    rows = [asdict(item) if isinstance(item, ValidationIssue) else dict(item) for item in issues]
    errors = sum(1 for item in rows if item["severity"] == "error")
    warnings = sum(1 for item in rows if item["severity"] == "warning")
    infos = sum(1 for item in rows if item["severity"] == "info")
    return {"valid": errors == 0, "error_count": errors, "warning_count": warnings, "info_count": infos, "issues": rows}


# ---------- contract assembly ----------

def _claim_statement(inp: GlobalImpactInput, metrics: Dict[str, Any]) -> str:
    if inp.claim_statement:
        return inp.claim_statement
    if inp.claim_type == "descriptive_observation":
        return f"{inp.indicator} was observed at {inp.current_value:g} {inp.unit} in {inp.current_period}."
    progress = metrics["progress_to_target_percent"]
    if progress is None:
        return f"Progress to target for {inp.indicator} could not be calculated from the entered baseline and target."
    return f"Estimated progress to target for {inp.indicator} is {progress:.2f}%."


def build_impact_contract(
    inp: GlobalImpactInput,
    *,
    generated_at: Optional[str] = None,
    strict: bool = False,
    migration: Optional[Dict[str, Any]] = None,
    runtime: str = "cross-runtime",
) -> Dict[str, Any]:
    timestamp = generated_at or inp.updated_at or inp.created_at or _iso_now()
    created_at = _normalize_timestamp(inp.created_at, timestamp)
    updated_at = _normalize_timestamp(inp.updated_at, timestamp)
    seed = _seed_material(inp)
    record_id = inp.record_id or stable_id("record", seed)
    entity_seed = record_id
    metrics = derive_metrics(inp)
    issues = validate_input(inp)
    validation = validation_result(issues)

    workspace = _entity("workspace", entity_seed, created_at, name=inp.workspace)
    initiative = _entity("initiative", entity_seed, created_at, workspace_id=workspace["id"], name=inp.initiative)
    goal = _entity("goal", entity_seed, created_at, initiative_id=initiative["id"], statement=inp.goal, sdg_theme=inp.sdg_theme)
    outcome = _entity("outcome", entity_seed, created_at, goal_id=goal["id"], statement=inp.outcome)
    definition = _entity(
        "indicator_definition_version", entity_seed, created_at,
        version="1.0", name=inp.indicator_definition, unit=inp.unit,
        direction="higher_is_better" if inp.higher_is_better else "lower_is_better",
    )
    indicator = _entity("indicator", entity_seed, created_at, outcome_id=outcome["id"], name=inp.indicator, definition_version=definition)
    source = _entity("source", entity_seed, created_at, title=inp.source, locator=inp.source_locator, source_type="entered_source")
    method = _entity(
        "method", entity_seed, created_at, name=inp.method_name, version=inp.method_version,
        description=inp.method_notes, design_type=inp.design_type,
    )
    baseline = _entity(
        "baseline", entity_seed, created_at, indicator_id=indicator["id"], value=inp.baseline_value,
        unit=inp.baseline_unit, period={"label": inp.baseline_period}, source_ids=[source["id"]], method_id=method["id"],
    )
    target = _entity(
        "target", entity_seed, created_at, indicator_id=indicator["id"], value=inp.target_value,
        unit=inp.target_unit, period={"label": inp.target_period}, direction=definition["direction"],
    )
    observation = _entity(
        "observation", entity_seed, created_at, indicator_id=indicator["id"], value=inp.current_value,
        unit=inp.current_unit, period={"label": inp.current_period}, source_ids=[source["id"]], method_id=method["id"],
    )
    population = _entity(
        "population_group", entity_seed, created_at, name=inp.population_group,
        observed_count=inp.beneficiaries,
    )
    geography = _entity("geography", entity_seed, created_at, name=inp.geography, geography_type="entered_label")
    budgets: List[Dict[str, Any]] = []
    if inp.budget_usd is not None:
        budgets.append(_entity("budget_record", entity_seed, created_at, initiative_id=initiative["id"], amount=inp.budget_usd, currency=inp.budget_currency, period={"label": inp.current_period}))

    interpretation_texts = [
        f"{inp.indicator} changed from {inp.baseline_value:g} {inp.unit} in {inp.baseline_period} to {inp.current_value:g} {inp.unit} in {inp.current_period}.",
        "Progress must be interpreted against the indicator definition, source, method, population, geography, confidence, and review status.",
        "Progress to target is unavailable because the baseline and target are not compatible." if metrics["progress_to_target_percent"] is None else f"Estimated progress to target is {metrics['progress_to_target_percent']:.2f}%.",
    ]
    if inp.confidence == "low":
        interpretation_texts.append("Confidence is low; treat this contract as preliminary until source and method review is complete.")
    interpretations = [
        _entity("interpretation", entity_seed + f"|{index}", created_at, interpretation_type="metric_interpretation", text=text, evidence_refs=[baseline["id"], observation["id"], target["id"]])
        for index, text in enumerate(interpretation_texts, start=1)
    ]

    claim_errors = [asdict(item) for item in issues if item.path.startswith("$.derived.claims") and item.severity == "error"]
    claim = _entity(
        "claim", entity_seed, created_at,
        claim_type=inp.claim_type,
        statement=_claim_statement(inp, metrics),
        confidence=inp.confidence,
        evidence_refs=[source["id"], method["id"], baseline["id"], observation["id"], target["id"]],
        design_metadata={
            "design_type": inp.design_type,
            "comparison_basis": inp.comparison_basis,
            "contribution_rationale": inp.contribution_rationale,
            "causal_design": inp.causal_design,
        },
        eligibility={"eligible": not claim_errors, "blocking_issue_ids": [item["issue_id"] for item in claim_errors]},
    )
    review = _entity("review", entity_seed, created_at, status=inp.review_status, confidence=inp.confidence, reviewer="not_recorded", notes="")
    revision = _entity("revision", entity_seed, created_at, revision_number=1, reason="Initial canonical contract", parent_revision_id=None)
    publications: List[Dict[str, Any]] = []
    if inp.review_status == "published":
        publications.append(_entity("publication", entity_seed, created_at, status="published", published_at=updated_at, title=inp.initiative))

    provenance: Dict[str, Any] = {
        "generated_by": {"name": "global-impact-catalyst", "version": ENGINE_VERSION, "runtime": runtime},
        "input_fingerprint": stable_token(seed),
        "source_contract_version": migration.get("source_contract_version") if migration else None,
        "migration": migration,
    }

    contract = {
        "contract_type": CONTRACT_TYPE,
        "contract_version": CONTRACT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "created_at": created_at,
        "updated_at": updated_at,
        "lifecycle_status": inp.review_status,
        "provenance": provenance,
        "facts": {
            "workspace": workspace,
            "initiative": initiative,
            "goal": goal,
            "outcomes": [outcome],
            "indicator": indicator,
            "measurement": {"baseline": baseline, "target": target, "observations": [observation]},
            "sources": [source],
            "methods": [method],
            "population_groups": [population],
            "geographies": [geography],
            "budget_records": budgets,
        },
        "derived": {"metrics": metrics, "interpretations": interpretations, "claims": [claim]},
        "governance": {"reviews": [review], "revisions": [revision], "publications": publications},
        "validation": validation,
        "traceability_path": list(TRACEABILITY_PATH),
        "boundaries": list(BOUNDARIES),
    }
    if strict and not validation["valid"]:
        raise ContractValidationError(validation["issues"])
    return contract


def build_impact_record(inp: GlobalImpactInput, *, generated_at: Optional[str] = None, strict: bool = False) -> Dict[str, Any]:
    """Backward-compatible alias returning the v1.1.0 canonical contract."""
    return build_impact_contract(inp, generated_at=generated_at, strict=strict)


def record_to_dict(record: Any) -> Dict[str, Any]:
    return asdict(record) if hasattr(record, "__dataclass_fields__") else dict(record)


def migrate_legacy_record(data: Dict[str, Any], *, generated_at: Optional[str] = None, strict: bool = False) -> Dict[str, Any]:
    """Migrate a v1.0.x flat record or compact input without discarding content."""
    if not isinstance(data, dict):
        raise InputValidationError("legacy record must be a JSON object")
    if data.get("contract_type") == CONTRACT_TYPE and data.get("contract_version") == CONTRACT_VERSION:
        return data
    payload = {
        "workspace": data.get("workspace", "Migrated workspace"),
        "initiative": data.get("initiative", ""),
        "goal": data.get("goal", ""),
        "outcome": data.get("outcome", data.get("goal", "")),
        "sdg_theme": data.get("sdg_theme", "Sustainable development"),
        "indicator": data.get("indicator", ""),
        "indicator_definition": data.get("indicator_definition", data.get("indicator", "")),
        "unit": data.get("unit", ""),
        "baseline_value": data.get("baseline_value", 0),
        "current_value": data.get("current_value", 0),
        "target_value": data.get("target_value", 100),
        "baseline_period": data.get("baseline_period", ""),
        "current_period": data.get("current_period", ""),
        "target_period": data.get("target_period", data.get("current_period", "")),
        "source": data.get("source", ""),
        "source_locator": data.get("source_locator", data.get("source", "")),
        "method_notes": data.get("method_notes", ""),
        "confidence": data.get("confidence", "medium"),
        "review_status": data.get("review_status", "draft"),
        "beneficiaries": data.get("beneficiaries"),
        "budget_usd": data.get("budget_usd"),
        "higher_is_better": data.get("higher_is_better", True),
        "claim_type": "progress_to_target_statement",
        "created_at": data.get("generated_at", generated_at or ""),
        "updated_at": data.get("generated_at", generated_at or ""),
    }
    migration = {
        "source_contract_version": data.get("contract_version", "1.0.x"),
        "migration_method": "lossless-flat-record-wrapper",
        "legacy_record": data,
    }
    return build_impact_contract(input_from_dict(payload), generated_at=generated_at or data.get("generated_at"), strict=strict, migration=migration)


def record_to_markdown(contract: Dict[str, Any]) -> str:
    facts = contract["facts"]
    metrics = contract["derived"]["metrics"]
    indicator = facts["indicator"]
    definition = indicator["definition_version"]
    measurement = facts["measurement"]
    source = facts["sources"][0]
    method = facts["methods"][0]
    validation = contract["validation"]
    lines = [
        f"# Global Impact Contract: {facts['initiative']['name']}", "",
        f"**Record ID:** `{contract['record_id']}`",
        f"**Contract:** {contract['contract_version']} · Schema {contract['schema_version']}",
        f"**Goal:** {facts['goal']['statement']}",
        f"**Outcome:** {facts['outcomes'][0]['statement']}",
        f"**Indicator:** {indicator['name']} ({definition['unit']})",
        f"**Direction:** {definition['direction'].replace('_', ' ')}",
        f"**Source:** {source['title']}",
        f"**Method:** {method['name']} v{method['version']} ({method['design_type'].replace('_', ' ')})",
        "", "## Entered Facts",
        f"- Baseline: {measurement['baseline']['value']:g} {measurement['baseline']['unit']} ({measurement['baseline']['period']['label']})",
        f"- Observation: {measurement['observations'][0]['value']:g} {measurement['observations'][0]['unit']} ({measurement['observations'][0]['period']['label']})",
        f"- Target: {measurement['target']['value']:g} {measurement['target']['unit']} ({measurement['target']['period']['label']})",
        "", "## Derived Metrics",
        f"- Absolute change: {metrics['absolute_change']:g} {definition['unit']}",
        f"- Percent change from baseline: {metrics['percent_change_from_baseline'] if metrics['percent_change_from_baseline'] is not None else 'n/a'}%",
        f"- Progress to target: {metrics['progress_to_target_percent'] if metrics['progress_to_target_percent'] is not None else 'n/a'}%",
        f"- Remaining gap: {metrics['remaining_gap']:g} {definition['unit']}",
        f"- Documentation/review signal: {metrics['data_quality_score']}/100",
        f"- Status: {metrics['status']}",
        "", "## Claim",
        f"- Type: {contract['derived']['claims'][0]['claim_type'].replace('_', ' ')}",
        f"- Statement: {contract['derived']['claims'][0]['statement']}",
        f"- Eligible: {'yes' if contract['derived']['claims'][0]['eligibility']['eligible'] else 'no'}",
        "", "## Validation",
        f"- Valid: {'yes' if validation['valid'] else 'no'}",
        f"- Errors: {validation['error_count']}",
        f"- Warnings: {validation['warning_count']}",
    ]
    lines.extend(f"- [{issue['severity']}] {issue['rule_id']}: {issue['message']} Remediation: {issue['remediation']}" for issue in validation["issues"])
    lines.extend(["", "## Interpretations"])
    lines.extend(f"- {item['text']}" for item in contract["derived"]["interpretations"])
    lines.extend(["", "## Boundaries"])
    lines.extend(f"- {item}" for item in contract["boundaries"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or migrate a Global Impact Catalyst v1.1.0 impact contract.")
    parser.add_argument("--input", required=True, help="Path to compact input or legacy record JSON")
    parser.add_argument("--output", required=True, help="Path to canonical contract JSON")
    parser.add_argument("--markdown", help="Optional Markdown contract brief")
    parser.add_argument("--generated-at", help="Optional fixed ISO-8601 timestamp")
    parser.add_argument("--migrate", action="store_true", help="Treat input as a legacy v1.0.x record")
    parser.add_argument("--allow-invalid", action="store_true", help="Write contracts containing validation errors")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    try:
        contract = migrate_legacy_record(data, generated_at=args.generated_at, strict=not args.allow_invalid) if args.migrate else build_impact_contract(input_from_dict(data), generated_at=args.generated_at, strict=not args.allow_invalid)
    except ContractValidationError as exc:
        print(json.dumps(validation_result(exc.issues), indent=2))
        return 2
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        md = Path(args.markdown)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(record_to_markdown(contract), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
