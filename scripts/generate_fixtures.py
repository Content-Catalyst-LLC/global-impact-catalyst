#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python.global_impact_core import build_impact_record, input_from_dict, record_to_dict

OUT = ROOT / "contracts/fixtures"
STAMP = "2026-07-17T16:00:00+00:00"
BASE = {
    "initiative": "Community Energy Retrofit Pilot",
    "goal": "Reduce household energy burden while improving residential efficiency.",
    "sdg_theme": "Affordable and clean energy",
    "indicator": "Average monthly bill reduction",
    "unit": "USD",
    "baseline_value": 0,
    "current_value": 18,
    "target_value": 30,
    "baseline_period": "2025 baseline",
    "current_period": "2026 Q2",
    "source": "Pilot utility-billing sample and participant survey summary",
    "method_notes": "Current value is the observed average monthly bill reduction across participating households compared with baseline average bills.",
    "confidence": "medium",
    "review_status": "needs_review",
    "beneficiaries": 420,
    "budget_usd": 125000,
    "higher_is_better": True,
}
CASES = {
    "01-higher-is-better": {},
    "02-lower-is-better-string-false": {"indicator": "Average monthly energy use", "unit": "kWh", "baseline_value": 100, "current_value": 70, "target_value": 50, "higher_is_better": "false"},
    "03-zero-baseline": {"baseline_value": 0, "current_value": 5, "target_value": 10},
    "04-equal-baseline-target": {"baseline_value": 10, "current_value": 10, "target_value": 10},
    "05-negative-progress": {"baseline_value": 10, "current_value": 5, "target_value": 20},
    "06-above-target": {"baseline_value": 10, "current_value": 25, "target_value": 20, "review_status": "reviewed"},
    "07-negative-decimals": {"baseline_value": -10.5, "current_value": -5.25, "target_value": 0, "budget_usd": 100.5, "beneficiaries": 3},
    "08-blank-evidence": {"source": "", "method_notes": "", "confidence": "low", "review_status": "draft"},
    "09-invalid-enums": {"confidence": "certain", "review_status": "approved"},
    "10-explicit-zero-optionals": {"beneficiaries": 0, "budget_usd": 0},
    "11-absent-optionals": {"beneficiaries": None, "budget_usd": None},
    "12-lower-is-better-reviewed": {"indicator": "Incident rate", "unit": "incidents", "baseline_value": 20, "current_value": 8, "target_value": 5, "higher_is_better": False, "confidence": "high", "review_status": "published"},
}
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob("*.json"):
    old.unlink()
for name, changes in CASES.items():
    payload = {**BASE, **changes}
    expected = record_to_dict(build_impact_record(input_from_dict(payload), generated_at=STAMP))
    fixture = {"name": name, "generated_at": STAMP, "input": payload, "expected": expected}
    (OUT / f"{name}.json").write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n")
print(f"Generated {len(CASES)} canonical fixtures.")
