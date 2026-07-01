"""Core logic for Global Impact Catalyst.

The module creates a traceable impact record from a small set of inputs.
It is intentionally dependency-light so it can run in educational, local,
and CI environments without a database or web server.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
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


@dataclass
class GlobalImpactMetrics:
    absolute_change: float
    percent_change_from_baseline: Optional[float]
    progress_to_target_percent: Optional[float]
    remaining_gap: float
    status: str
    cost_per_beneficiary_usd: Optional[float]
    data_quality_score: int


@dataclass
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


def _clean_confidence(value: str) -> str:
    value = (value or "medium").strip().lower()
    return value if value in {"low", "medium", "high"} else "medium"


def _clean_review_status(value: str) -> str:
    value = (value or "draft").strip().lower().replace(" ", "_")
    allowed = {"draft", "needs_review", "reviewed", "published"}
    return value if value in allowed else "draft"


def _safe_percent(numerator: float, denominator: float) -> Optional[float]:
    if denominator == 0:
        return None
    return (numerator / denominator) * 100.0


def _progress_to_target(inp: GlobalImpactInput) -> Optional[float]:
    distance = inp.target_value - inp.baseline_value
    if distance == 0:
        return None
    if inp.higher_is_better:
        progress = (inp.current_value - inp.baseline_value) / distance
    else:
        progress = (inp.baseline_value - inp.current_value) / (inp.baseline_value - inp.target_value)
    return round(progress * 100.0, 2)


def _status(progress: Optional[float], confidence: str, review_status: str) -> str:
    if progress is None:
        return "needs baseline/target review"
    if review_status in {"draft", "needs_review"}:
        prefix = "draft — "
    else:
        prefix = "reviewed — "
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


def _data_quality_score(inp: GlobalImpactInput) -> int:
    score = 0
    if inp.source.strip():
        score += 25
    if inp.method_notes.strip() and len(inp.method_notes.strip()) >= 20:
        score += 25
    if _clean_confidence(inp.confidence) == "high":
        score += 25
    elif _clean_confidence(inp.confidence) == "medium":
        score += 15
    else:
        score += 5
    if _clean_review_status(inp.review_status) in {"reviewed", "published"}:
        score += 25
    elif _clean_review_status(inp.review_status) == "needs_review":
        score += 10
    return min(score, 100)


def build_impact_record(inp: GlobalImpactInput) -> GlobalImpactRecord:
    confidence = _clean_confidence(inp.confidence)
    review_status = _clean_review_status(inp.review_status)
    absolute_change = inp.current_value - inp.baseline_value
    percent_change = _safe_percent(absolute_change, inp.baseline_value)
    progress = _progress_to_target(inp)
    remaining_gap = inp.target_value - inp.current_value if inp.higher_is_better else inp.current_value - inp.target_value
    cost_per_beneficiary = None
    if inp.beneficiaries and inp.beneficiaries > 0 and inp.budget_usd is not None:
        cost_per_beneficiary = round(inp.budget_usd / inp.beneficiaries, 2)

    metrics = GlobalImpactMetrics(
        absolute_change=round(absolute_change, 4),
        percent_change_from_baseline=None if percent_change is None else round(percent_change, 2),
        progress_to_target_percent=progress,
        remaining_gap=round(remaining_gap, 4),
        status=_status(progress, confidence, review_status),
        cost_per_beneficiary_usd=cost_per_beneficiary,
        data_quality_score=_data_quality_score(inp),
    )

    interpretation = [
        f"{inp.indicator} changed from {inp.baseline_value:g} {inp.unit} in {inp.baseline_period} to {inp.current_value:g} {inp.unit} in {inp.current_period}.",
        "Progress should be interpreted against the indicator definition, data source, method notes, and confidence level.",
    ]
    if progress is not None:
        interpretation.append(f"Estimated progress to target is {progress:.2f}%.")
    if confidence == "low":
        interpretation.append("Confidence is low, so this record should be treated as preliminary until the source and method are reviewed.")
    if review_status in {"draft", "needs_review"}:
        interpretation.append("Review status indicates that this output is not final.")

    return GlobalImpactRecord(
        record_type="global_impact_catalyst_record",
        generated_at=datetime.now(timezone.utc).isoformat(),
        initiative=inp.initiative,
        goal=inp.goal,
        sdg_theme=inp.sdg_theme,
        indicator=inp.indicator,
        unit=inp.unit,
        baseline_period=inp.baseline_period,
        current_period=inp.current_period,
        baseline_value=inp.baseline_value,
        current_value=inp.current_value,
        target_value=inp.target_value,
        higher_is_better=inp.higher_is_better,
        source=inp.source,
        method_notes=inp.method_notes,
        confidence=confidence,
        review_status=review_status,
        beneficiaries=inp.beneficiaries,
        budget_usd=inp.budget_usd,
        metrics=metrics,
        interpretation_notes=interpretation,
        traceability_path=[
            "goal",
            "indicator",
            "baseline",
            "current measurement",
            "target",
            "source",
            "method notes",
            "confidence",
            "review status",
        ],
        boundaries=[
            "This record is not an ESG assurance opinion or SDG certification.",
            "Results depend on data quality, source reliability, indicator definition, and method choices.",
            "Human review is required before formal reporting or external claims.",
        ],
    )


def input_from_dict(data: Dict[str, Any]) -> GlobalImpactInput:
    return GlobalImpactInput(
        initiative=str(data.get("initiative", "Untitled initiative")),
        goal=str(data.get("goal", "Clarify impact goal")),
        sdg_theme=str(data.get("sdg_theme", "Sustainable development")),
        indicator=str(data.get("indicator", "Indicator")),
        unit=str(data.get("unit", "units")),
        baseline_value=float(data.get("baseline_value", 0)),
        current_value=float(data.get("current_value", 0)),
        target_value=float(data.get("target_value", 100)),
        baseline_period=str(data.get("baseline_period", "baseline")),
        current_period=str(data.get("current_period", "current")),
        source=str(data.get("source", "")),
        method_notes=str(data.get("method_notes", "")),
        confidence=str(data.get("confidence", "medium")),
        review_status=str(data.get("review_status", "draft")),
        beneficiaries=None if data.get("beneficiaries") in {None, ""} else int(data.get("beneficiaries")),
        budget_usd=None if data.get("budget_usd") in {None, ""} else float(data.get("budget_usd")),
        higher_is_better=bool(data.get("higher_is_better", True)),
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
        f"- Data quality score: {metrics.data_quality_score}/100",
        f"- Status: {metrics.status}",
        "",
        "## Interpretation Notes",
    ]
    for note in record.interpretation_notes:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Method Notes",
        record.method_notes,
        "",
        "## Boundaries",
    ])
    for boundary in record.boundaries:
        lines.append(f"- {boundary}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Global Impact Catalyst impact record.")
    parser.add_argument("--input", required=True, help="Path to JSON input file")
    parser.add_argument("--output", required=True, help="Path to JSON output file")
    parser.add_argument("--markdown", help="Optional Markdown brief output path")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    record = build_impact_record(input_from_dict(data))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record_to_dict(record), indent=2), encoding="utf-8")

    if args.markdown:
        md = Path(args.markdown)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(record_to_markdown(record), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
