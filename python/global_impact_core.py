"""Canonical Global Impact Catalyst v1.0.1 computation engine.

The module creates a traceable impact record from a small set of inputs. It is
intentionally dependency-light so it can run in educational, local, and CI
environments without a database or web server.

Python and browser implementations are governed by the same fixtures, output
schema, status language, interpretation notes, traceability path, boundaries,
and rounding rules.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional

ENGINE_VERSION = "1.0.1"
RECORD_TYPE = "global_impact_catalyst_record"
CONFIDENCE_VALUES = {"low", "medium", "high"}
REVIEW_STATUS_VALUES = {"draft", "needs_review", "reviewed", "published"}
TRACEABILITY_PATH = [
    "goal",
    "indicator",
    "baseline",
    "current measurement",
    "target",
    "source",
    "method notes",
    "confidence",
    "review status",
]
BOUNDARIES = [
    "This record is not an ESG assurance opinion or SDG certification.",
    "Results depend on data quality, source reliability, indicator definition, and method choices.",
    "Human review is required before formal reporting or external claims.",
]


class InputValidationError(ValueError):
    """Raised when an input cannot be converted to the canonical contract."""


@dataclass(frozen=True)
class GlobalImpactInput:
    initiative: str
    goal: str
    sdg_theme: str
    indicator: str
    unit: str
    baseline_value: float
    current_value: float
    target_value: float
    baseline_period: str
    current_period: str
    source: str
    method_notes: str
    confidence: str = "medium"
    review_status: str = "draft"
    beneficiaries: Optional[int] = None
    budget_usd: Optional[float] = None
    higher_is_better: bool = True


@dataclass(frozen=True)
class DataQualityComponents:
    source_documented: int
    method_documented: int
    confidence_signal: int
    review_signal: int


@dataclass(frozen=True)
class GlobalImpactMetrics:
    absolute_change: float
    percent_change_from_baseline: Optional[float]
    progress_to_target_percent: Optional[float]
    remaining_gap: float
    status: str
    cost_per_beneficiary_usd: Optional[float]
    data_quality_score: int
    data_quality_components: DataQualityComponents


@dataclass(frozen=True)
class GlobalImpactRecord:
    record_type: str
    generated_at: str
    initiative: str
    goal: str
    sdg_theme: str
    indicator: str
    unit: str
    baseline_period: str
    current_period: str
    baseline_value: float
    current_value: float
    target_value: float
    higher_is_better: bool
    source: str
    method_notes: str
    confidence: str
    review_status: str
    beneficiaries: Optional[int]
    budget_usd: Optional[float]
    metrics: GlobalImpactMetrics
    interpretation_notes: List[str]
    traceability_path: List[str]
    boundaries: List[str]


def _round(value: float, places: int) -> float:
    """Round halves away from zero using a cross-runtime documented rule."""
    quantum = Decimal("1").scaleb(-places)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def _clean_confidence(value: Any) -> str:
    cleaned = str(value if value is not None else "medium").strip().lower()
    return cleaned if cleaned in CONFIDENCE_VALUES else "medium"


def _clean_review_status(value: Any) -> str:
    cleaned = str(value if value is not None else "draft").strip().lower().replace(" ", "_")
    return cleaned if cleaned in REVIEW_STATUS_VALUES else "draft"


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
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    number = _parse_number(value, field=field)
    if not number.is_integer():
        raise InputValidationError(f"{field} must be an integer")
    integer = int(number)
    if integer < minimum:
        raise InputValidationError(f"{field} must be greater than or equal to {minimum}")
    return integer


def _text(data: Dict[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if value is None:
        value = default
    return str(value).strip()


def _safe_percent(numerator: float, denominator: float) -> Optional[float]:
    if denominator == 0:
        return None
    return (numerator / denominator) * 100.0


def _progress_to_target(inp: GlobalImpactInput) -> Optional[float]:
    if inp.higher_is_better:
        denominator = inp.target_value - inp.baseline_value
        numerator = inp.current_value - inp.baseline_value
    else:
        denominator = inp.baseline_value - inp.target_value
        numerator = inp.baseline_value - inp.current_value
    progress = _safe_percent(numerator, denominator)
    return None if progress is None else _round(progress, 2)


def _status(progress: Optional[float], confidence: str, review_status: str) -> str:
    if progress is None:
        return "needs baseline/target review"
    prefix = "draft — " if review_status in {"draft", "needs_review"} else "reviewed — "
    if confidence == "low":
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


def _data_quality_components(inp: GlobalImpactInput) -> DataQualityComponents:
    source_documented = 25 if inp.source.strip() else 0
    method_documented = 25 if len(inp.method_notes.strip()) >= 20 else 0
    confidence_signal = {"high": 25, "medium": 15, "low": 5}[inp.confidence]
    review_signal = 25 if inp.review_status in {"reviewed", "published"} else 10 if inp.review_status == "needs_review" else 0
    return DataQualityComponents(
        source_documented=source_documented,
        method_documented=method_documented,
        confidence_signal=confidence_signal,
        review_signal=review_signal,
    )


def build_impact_record(inp: GlobalImpactInput, *, generated_at: Optional[str] = None) -> GlobalImpactRecord:
    confidence = _clean_confidence(inp.confidence)
    review_status = _clean_review_status(inp.review_status)
    normalized = GlobalImpactInput(
        **{
            **asdict(inp),
            "confidence": confidence,
            "review_status": review_status,
        }
    )
    absolute_change = normalized.current_value - normalized.baseline_value
    percent_change = _safe_percent(absolute_change, normalized.baseline_value)
    progress = _progress_to_target(normalized)
    remaining_gap = (
        normalized.target_value - normalized.current_value
        if normalized.higher_is_better
        else normalized.current_value - normalized.target_value
    )
    cost_per_beneficiary = None
    if normalized.beneficiaries is not None and normalized.beneficiaries > 0 and normalized.budget_usd is not None:
        cost_per_beneficiary = _round(normalized.budget_usd / normalized.beneficiaries, 2)

    quality_components = _data_quality_components(normalized)
    metrics = GlobalImpactMetrics(
        absolute_change=_round(absolute_change, 4),
        percent_change_from_baseline=None if percent_change is None else _round(percent_change, 2),
        progress_to_target_percent=progress,
        remaining_gap=_round(remaining_gap, 4),
        status=_status(progress, confidence, review_status),
        cost_per_beneficiary_usd=cost_per_beneficiary,
        data_quality_score=min(sum(asdict(quality_components).values()), 100),
        data_quality_components=quality_components,
    )

    interpretation = [
        f"{normalized.indicator} changed from {normalized.baseline_value:g} {normalized.unit} in {normalized.baseline_period} to {normalized.current_value:g} {normalized.unit} in {normalized.current_period}.",
        "Progress should be interpreted against the indicator definition, data source, method notes, confidence level, and review status.",
        (
            "Progress to target could not be calculated because the baseline and target need review."
            if progress is None
            else f"Estimated progress to target is {progress:.2f}%."
        ),
    ]
    if confidence == "low":
        interpretation.append("Confidence is low, so this record should be treated as preliminary until the source and method are reviewed.")
    if review_status in {"draft", "needs_review"}:
        interpretation.append("Review status indicates that this output is not final.")

    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    return GlobalImpactRecord(
        record_type=RECORD_TYPE,
        generated_at=timestamp,
        initiative=normalized.initiative,
        goal=normalized.goal,
        sdg_theme=normalized.sdg_theme,
        indicator=normalized.indicator,
        unit=normalized.unit,
        baseline_period=normalized.baseline_period,
        current_period=normalized.current_period,
        baseline_value=normalized.baseline_value,
        current_value=normalized.current_value,
        target_value=normalized.target_value,
        higher_is_better=normalized.higher_is_better,
        source=normalized.source,
        method_notes=normalized.method_notes,
        confidence=confidence,
        review_status=review_status,
        beneficiaries=normalized.beneficiaries,
        budget_usd=normalized.budget_usd,
        metrics=metrics,
        interpretation_notes=interpretation,
        traceability_path=list(TRACEABILITY_PATH),
        boundaries=list(BOUNDARIES),
    )


def input_from_dict(data: Dict[str, Any]) -> GlobalImpactInput:
    if not isinstance(data, dict):
        raise InputValidationError("input must be a JSON object")
    return GlobalImpactInput(
        initiative=_text(data, "initiative", "Untitled initiative"),
        goal=_text(data, "goal", "Clarify impact goal"),
        sdg_theme=_text(data, "sdg_theme", "Sustainable development"),
        indicator=_text(data, "indicator", "Indicator"),
        unit=_text(data, "unit", "units"),
        baseline_value=_parse_number(data.get("baseline_value"), field="baseline_value", default=0),
        current_value=_parse_number(data.get("current_value"), field="current_value", default=0),
        target_value=_parse_number(data.get("target_value"), field="target_value", default=100),
        baseline_period=_text(data, "baseline_period", "baseline"),
        current_period=_text(data, "current_period", "current"),
        source=_text(data, "source", ""),
        method_notes=_text(data, "method_notes", ""),
        confidence=_clean_confidence(data.get("confidence", "medium")),
        review_status=_clean_review_status(data.get("review_status", "draft")),
        beneficiaries=_parse_optional_integer(data.get("beneficiaries"), field="beneficiaries"),
        budget_usd=_parse_optional_number(data.get("budget_usd"), field="budget_usd"),
        higher_is_better=_parse_boolean(data.get("higher_is_better", True), field="higher_is_better", default=True),
    )


def record_to_dict(record: GlobalImpactRecord) -> Dict[str, Any]:
    return asdict(record)


def record_to_markdown(record: GlobalImpactRecord) -> str:
    metrics = record.metrics
    lines = [
        f"# Global Impact Catalyst Brief: {record.initiative}",
        "",
        f"**Goal:** {record.goal}",
        f"**Theme:** {record.sdg_theme}",
        f"**Indicator:** {record.indicator} ({record.unit})",
        f"**Period:** {record.baseline_period} → {record.current_period}",
        f"**Source:** {record.source}",
        f"**Confidence:** {record.confidence}",
        f"**Review status:** {record.review_status}",
        "",
        "## Metrics",
        f"- Baseline: {record.baseline_value:g} {record.unit}",
        f"- Current: {record.current_value:g} {record.unit}",
        f"- Target: {record.target_value:g} {record.unit}",
        f"- Absolute change: {metrics.absolute_change:g} {record.unit}",
        f"- Percent change from baseline: {metrics.percent_change_from_baseline if metrics.percent_change_from_baseline is not None else 'n/a'}%",
        f"- Progress to target: {metrics.progress_to_target_percent if metrics.progress_to_target_percent is not None else 'n/a'}%",
        f"- Remaining gap: {metrics.remaining_gap:g} {record.unit}",
        f"- Data completeness/review signal: {metrics.data_quality_score}/100",
        f"- Status: {metrics.status}",
        "",
        "## Data Completeness and Review Components",
        f"- Source documented: {metrics.data_quality_components.source_documented}/25",
        f"- Method documented: {metrics.data_quality_components.method_documented}/25",
        f"- Confidence signal: {metrics.data_quality_components.confidence_signal}/25",
        f"- Review signal: {metrics.data_quality_components.review_signal}/25",
        "",
        "The score above is a documentation and review heuristic. It is not an objective rating of evidence quality, assurance, or truth.",
        "",
        "## Interpretation Notes",
    ]
    lines.extend(f"- {note}" for note in record.interpretation_notes)
    lines.extend(["", "## Method Notes", record.method_notes, "", "## Boundaries"])
    lines.extend(f"- {boundary}" for boundary in record.boundaries)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Global Impact Catalyst impact record.")
    parser.add_argument("--input", required=True, help="Path to JSON input file")
    parser.add_argument("--output", required=True, help="Path to JSON output file")
    parser.add_argument("--markdown", help="Optional Markdown brief output path")
    parser.add_argument("--generated-at", help="Optional fixed ISO-8601 timestamp for reproducible outputs")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    record = build_impact_record(input_from_dict(data), generated_at=args.generated_at)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record_to_dict(record), indent=2) + "\n", encoding="utf-8")

    if args.markdown:
        md = Path(args.markdown)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(record_to_markdown(record), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
