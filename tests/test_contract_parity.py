from __future__ import annotations
import json
from pathlib import Path
from python.global_impact_core import build_impact_contract,input_from_dict
ROOT=Path(__file__).resolve().parents[1]

def test_python_matches_all_golden_contract_fixtures():
    files=sorted((ROOT/'contracts/fixtures').glob('*.json'))
    assert len(files)>=15
    for path in files:
        fixture=json.loads(path.read_text())
        actual=build_impact_contract(input_from_dict(fixture['input']),generated_at=fixture['generated_at'])
        assert actual==fixture['expected'],path.name
