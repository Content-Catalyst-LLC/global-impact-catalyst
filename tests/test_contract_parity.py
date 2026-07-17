from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from python.global_impact_core import build_impact_record, input_from_dict, record_to_dict

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "contracts/fixtures"


def test_python_matches_all_golden_fixtures():
    files = sorted(FIXTURES.glob("*.json"))
    assert len(files) >= 10
    for path in files:
        fixture = json.loads(path.read_text())
        actual = record_to_dict(build_impact_record(input_from_dict(fixture["input"]), generated_at=fixture["generated_at"]))
        assert actual == fixture["expected"], path.name


def test_browser_matches_all_golden_fixtures():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is not installed")
    subprocess.run([node, "scripts/check_browser_parity.js"], cwd=ROOT, check=True)
