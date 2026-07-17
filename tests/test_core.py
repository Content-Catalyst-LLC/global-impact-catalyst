from __future__ import annotations
import json
from pathlib import Path
import pytest
from python.global_impact_core import (
    ContractValidationError, InputValidationError, build_impact_contract,
    build_impact_record, input_from_dict, migrate_legacy_record,
    record_to_markdown, stable_id, stable_token, validation_result,
)

STAMP='2026-07-17T18:00:00+00:00'
BASE={
 'workspace':'Impact Portfolio','initiative':'Energy Pilot','goal':'Reduce energy burden.',
 'outcome':'Households pay less for energy.','sdg_theme':'Affordable and clean energy',
 'indicator':'Average bill reduction','indicator_definition':'Mean monthly bill reduction.',
 'unit':'USD','baseline_value':0,'current_value':18,'target_value':30,
 'baseline_period':'2025','current_period':'2026 Q2','target_period':'2027',
 'source':'Billing dataset','source_locator':'dataset:gic-energy-q2',
 'method_name':'Billing comparison','method_version':'1.0','design_type':'before_after',
 'method_notes':'Compare participant bills with their documented baseline after normalization.',
 'confidence':'medium','review_status':'needs_review','beneficiaries':100,
 'population_group':'Participating households','geography':'Chicago, Illinois',
 'budget_usd':10000,'budget_currency':'USD','higher_is_better':True,
 'claim_type':'progress_to_target_statement','claim_statement':''
}

def contract(**changes):
    return build_impact_contract(input_from_dict({**BASE,**changes}),generated_at=STAMP)

def test_contract_identity_and_versions_are_stable():
    first=contract(); second=contract()
    assert first['record_id']==second['record_id']
    assert first['contract_type']=='global_impact_contract'
    assert first['contract_version']=='1.1.0'
    assert first['schema_version']=='1.1.0'
    assert first['created_at']==STAMP==first['updated_at']

def test_stable_id_helpers_are_deterministic():
    assert stable_token('abc')==stable_token('abc')
    assert stable_id('record','abc').startswith('gic-record-')
    assert len(stable_id('record','abc').split('-')[-1])==16

def test_all_material_entities_have_ids_and_timestamps():
    value=contract(review_status='published')
    entities=[]
    f=value['facts']
    entities += [f['workspace'],f['initiative'],f['goal'],f['indicator'],f['indicator']['definition_version']]
    entities += f['outcomes'] + [f['measurement']['baseline'],f['measurement']['target']] + f['measurement']['observations']
    entities += f['sources']+f['methods']+f['population_groups']+f['geographies']+f['budget_records']
    entities += value['derived']['interpretations']+value['derived']['claims']
    entities += value['governance']['reviews']+value['governance']['revisions']+value['governance']['publications']
    for entity in entities:
        assert entity['id'].startswith('gic-')
        assert entity['created_at']==STAMP
        assert entity['updated_at']==STAMP

def test_facts_and_derived_values_are_separate():
    value=contract()
    assert 'metrics' not in value['facts']
    assert value['facts']['measurement']['observations'][0]['value']==18
    assert value['derived']['metrics']['progress_to_target_percent']==60.0
    assert value['derived']['metrics']['calculation_method']['engine_version']=='1.1.0'

def test_lower_is_better_progress_and_false_string():
    value=contract(baseline_value=100,current_value=70,target_value=50,higher_is_better='false')
    assert value['facts']['indicator']['definition_version']['direction']=='lower_is_better'
    assert value['derived']['metrics']['progress_to_target_percent']==60.0
    assert value['derived']['metrics']['remaining_gap']==20.0

def test_optional_zero_is_distinct_from_absent():
    zero=contract(beneficiaries=0,budget_usd=0)
    absent=contract(beneficiaries=None,budget_usd=None)
    assert zero['facts']['population_groups'][0]['observed_count']==0
    assert len(zero['facts']['budget_records'])==1
    assert zero['derived']['metrics']['cost_per_beneficiary'] is None
    assert absent['facts']['population_groups'][0]['observed_count'] is None
    assert absent['facts']['budget_records']==[]

def test_structured_required_field_errors_are_actionable():
    value=contract(initiative='',source='',source_locator='',method_notes='')
    result=value['validation']
    assert result['valid'] is False
    assert result['error_count']>=3
    issue=result['issues'][0]
    assert set(issue)=={'issue_id','severity','path','rule_id','message','remediation'}
    assert issue['rule_id']=='GIC-REQ-001'

def test_period_ordering_validation():
    value=contract(baseline_period='2027',current_period='2026 Q2')
    assert any(i['rule_id']=='GIC-PERIOD-001' and i['severity']=='error' for i in value['validation']['issues'])

def test_unparseable_periods_warn_not_error():
    value=contract(baseline_period='before launch',current_period='follow-up')
    assert value['validation']['valid'] is True
    assert any(i['rule_id']=='GIC-PERIOD-002' and i['severity']=='warning' for i in value['validation']['issues'])

def test_unit_compatibility_validation():
    value=contract(current_unit='EUR')
    assert any(i['rule_id']=='GIC-UNIT-001' for i in value['validation']['issues'])

def test_indicator_direction_and_target_compatibility():
    higher=contract(baseline_value=100,target_value=50,higher_is_better=True)
    lower=contract(baseline_value=50,target_value=100,higher_is_better=False)
    equal=contract(baseline_value=10,target_value=10)
    assert any(i['rule_id']=='GIC-DIRECTION-001' for i in higher['validation']['issues'])
    assert any(i['rule_id']=='GIC-DIRECTION-002' for i in lower['validation']['issues'])
    assert any(i['rule_id']=='GIC-TARGET-001' for i in equal['validation']['issues'])

def test_comparison_claim_requires_design_and_basis():
    blocked=contract(claim_type='comparison',claim_statement='Participants improved more.',design_type='before_after')
    rules={i['rule_id'] for i in blocked['validation']['issues']}
    assert {'GIC-CLAIM-COMP-001','GIC-CLAIM-COMP-002'} <= rules
    assert blocked['derived']['claims'][0]['eligibility']['eligible'] is False
    eligible=contract(claim_type='comparison',claim_statement='Participants improved more than matched controls.',design_type='comparison_group',comparison_basis='Matched controls')
    assert eligible['derived']['claims'][0]['eligibility']['eligible'] is True

def test_contribution_claim_requires_rationale():
    value=contract(claim_type='contribution_statement',claim_statement='The pilot contributed.',design_type='monitoring')
    rules={i['rule_id'] for i in value['validation']['issues']}
    assert 'GIC-CLAIM-CONTRIB-001' in rules
    assert 'GIC-CLAIM-CONTRIB-002' in rules

def test_causal_claim_gate_and_eligible_case():
    blocked=contract(claim_type='causal_claim',claim_statement='The pilot caused change.',design_type='before_after',confidence='medium',review_status='draft')
    rules={i['rule_id'] for i in blocked['validation']['issues']}
    assert {'GIC-CLAIM-CAUSAL-001','GIC-CLAIM-CAUSAL-002','GIC-CLAIM-CAUSAL-003','GIC-CLAIM-CAUSAL-004'} <= rules
    eligible=contract(claim_type='causal_claim',claim_statement='Random assignment caused the change.',design_type='randomized',causal_design='Random assignment with intent-to-treat analysis.',confidence='high',review_status='reviewed')
    assert eligible['validation']['valid'] is True
    assert eligible['derived']['claims'][0]['eligibility']['eligible'] is True

def test_strict_mode_raises_with_structured_issues():
    with pytest.raises(ContractValidationError) as exc:
        build_impact_contract(input_from_dict({**BASE,'source':''}),generated_at=STAMP,strict=True)
    assert exc.value.issues[0]['severity']=='error'

def test_backward_alias_returns_canonical_contract():
    value=build_impact_record(input_from_dict(BASE),generated_at=STAMP)
    assert value['contract_type']=='global_impact_contract'

def test_legacy_migration_preserves_original_record_losslessly():
    legacy=json.loads(Path('contracts/legacy/legacy-v1.0.1-record.json').read_text())
    migrated=migrate_legacy_record(legacy,strict=False)
    migration=migrated['provenance']['migration']
    assert migration['legacy_record']==legacy
    assert migration['source_contract_version']=='1.0.x'
    assert migrated['facts']['initiative']['name']==legacy['initiative']
    assert migrated['facts']['measurement']['baseline']['value']==legacy['baseline_value']
    assert migrated['derived']['metrics']['progress_to_target_percent']==legacy['metrics']['progress_to_target_percent']

def test_markdown_exposes_contract_validation_and_boundaries():
    text=record_to_markdown(contract())
    assert '# Global Impact Contract:' in text
    assert '## Entered Facts' in text
    assert '## Derived Metrics' in text
    assert '## Validation' in text
    assert '## Boundaries' in text

def test_invalid_boolean_and_numbers_raise_normalization_errors():
    with pytest.raises(InputValidationError): input_from_dict({**BASE,'higher_is_better':'sometimes'})
    with pytest.raises(InputValidationError): input_from_dict({**BASE,'beneficiaries':1.5})
    with pytest.raises(InputValidationError): input_from_dict({**BASE,'budget_usd':-1})

def test_validation_result_counts_levels():
    result=validation_result([
      {'issue_id':'1','severity':'error','path':'$','rule_id':'GIC-X','message':'x','remediation':'x'},
      {'issue_id':'2','severity':'warning','path':'$','rule_id':'GIC-Y','message':'y','remediation':'y'}])
    assert result=={'valid':False,'error_count':1,'warning_count':1,'info_count':0,'issues':result['issues']}
