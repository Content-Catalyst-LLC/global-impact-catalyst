from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_core import build_impact_record, input_from_dict, record_to_dict

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    return json.loads((ROOT / name).read_text())


def test_schemas_are_valid():
    Draft202012Validator.check_schema(load("schemas/global_impact_input.schema.json"))
    Draft202012Validator.check_schema(load("schemas/global_impact_record.schema.json"))


def test_sample_input_and_generated_output_validate():
    input_schema = load("schemas/global_impact_input.schema.json")
    output_schema = load("schemas/global_impact_record.schema.json")
    sample = load("data/sample_global_impact_input.json")
    Draft202012Validator(input_schema).validate(sample)
    record = record_to_dict(build_impact_record(input_from_dict(sample), generated_at="2026-07-17T16:00:00+00:00"))
    Draft202012Validator(output_schema, format_checker=FormatChecker()).validate(record)


def test_examples_validate():
    output_schema = load("schemas/global_impact_record.schema.json")
    example = load("examples/example_global_impact_record.json")
    Draft202012Validator(output_schema, format_checker=FormatChecker()).validate(example)


def test_all_fixture_outputs_validate():
    output_schema = load("schemas/global_impact_record.schema.json")
    validator = Draft202012Validator(output_schema, format_checker=FormatChecker())
    for fixture_path in sorted((ROOT / "contracts/fixtures").glob("*.json")):
        fixture = json.loads(fixture_path.read_text())
        validator.validate(fixture["expected"])
