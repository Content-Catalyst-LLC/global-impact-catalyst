from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/'schemas'/name).read_text())
def validator(name): return Draft202012Validator(load(name),format_checker=FormatChecker())

def test_canonical_schemas_remain_v110_and_repository_schemas_are_versioned():
    for name in ['global_impact_input.schema.json','global_impact_contract.schema.json','global_impact_record.schema.json','global_impact_validation_result.schema.json']:
        schema=load(name)
        assert schema['x-global-impact-catalyst-version']=='1.1.0'
        assert '/1.1.0/' in schema['$id']
    schema=load('global_impact_indicator_registry.schema.json')
    assert schema['x-global-impact-catalyst-version']=='1.4.0'
    assert '/1.4.0/' in schema['$id']
    schema=load('global_impact_workspace_bundle.schema.json')
    assert schema['x-global-impact-catalyst-version']=='1.7.0'
    assert '/1.7.0/' in schema['$id']
    schema=load('global_impact_review_workflow.schema.json')
    assert schema['x-global-impact-catalyst-version']=='1.6.0'
    assert '/1.6.0/' in schema['$id']
    analysis=load('global_impact_analysis_repository.schema.json')
    assert analysis['x-global-impact-catalyst-version']=='1.7.0'
    assert '/1.7.0/' in analysis['$id']
    for name in ['global_impact_measurement_repository.schema.json','global_impact_outcome_portfolio_aggregation.schema.json','global_impact_beneficiary_summary.schema.json']:
        schema=load(name)
        assert schema['x-global-impact-catalyst-version']=='1.5.0'
        assert '/1.5.0/' in schema['$id']
    for name in ['global_impact_evidence_chain.schema.json','global_impact_evidence_repository.schema.json']:
        schema=load(name)
        assert schema['x-global-impact-catalyst-version']=='1.3.0'
        assert '/1.3.0/' in schema['$id']

def test_all_canonical_fixture_outputs_validate():
    check=validator('global_impact_contract.schema.json')
    for path in sorted((ROOT/'contracts/fixtures').glob('*.json')):
        expected=json.loads(path.read_text())['expected']
        errors=list(check.iter_errors(expected))
        assert not errors, f"{path.name}: {[e.message for e in errors]}"

def test_validation_objects_validate_independently():
    check=validator('global_impact_validation_result.schema.json')
    for path in sorted((ROOT/'contracts/fixtures').glob('*.json')):
        expected=json.loads(path.read_text())['expected']['validation']
        assert not list(check.iter_errors(expected))

def test_sample_authoring_input_validates():
    sample=json.loads((ROOT/'data/sample_global_impact_input.json').read_text())
    errors=list(validator('global_impact_input.schema.json').iter_errors(sample))
    assert not errors,[e.message for e in errors]

def test_workspace_bundle_example_validates():
    bundle=json.loads((ROOT/'examples/example_global_impact_workspace_bundle.json').read_text())
    errors=list(validator('global_impact_workspace_bundle.schema.json').iter_errors(bundle))
    assert not errors,[e.message for e in errors]

def test_contract_schema_rejects_flat_v101_record():
    legacy=json.loads((ROOT/'contracts/legacy/legacy-v1.0.1-record.json').read_text())
    assert list(validator('global_impact_contract.schema.json').iter_errors(legacy))

def test_contract_schema_rejects_unknown_fields():
    fixture=json.loads(next((ROOT/'contracts/fixtures').glob('*.json')).read_text())['expected']
    fixture['unexpected']=True
    assert list(validator('global_impact_contract.schema.json').iter_errors(fixture))

