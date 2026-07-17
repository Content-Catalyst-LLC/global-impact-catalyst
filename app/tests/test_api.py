from app.main import build_demo_response,healthcheck,validate_demo_payload

PAYLOAD={'initiative':'Pilot','goal':'Improve outcomes','indicator':'Rate','unit':'%','baseline_value':10,'current_value':20,'target_value':30,'baseline_period':'2025','current_period':'2026','source':'Dataset','method_notes':'A documented method with enough detail for review.'}

def test_demo_response_is_canonical_contract():
    response=build_demo_response(PAYLOAD,generated_at='2026-07-17T18:00:00+00:00')
    assert response['contract_type']=='global_impact_contract'
    assert response['contract_version']=='1.1.0'

def test_validate_demo_payload_returns_structured_result():
    result=validate_demo_payload({**PAYLOAD,'source':''})
    assert result['valid'] is False
    assert result['issues'][0]['rule_id']=='GIC-REQ-001'

def test_healthcheck_version():
    assert healthcheck()=={'status':'ok','module':'global-impact-catalyst','version':'1.7.0','contract_version':'1.1.0','database_schema_version':8,'persistence':'sqlite','evidence_repository':'sources-provenance-evidence','indicator_registry':'units-baselines-targets-methods','indicator_registry_version':'1.4.0','measurement_repository':'observations-beneficiaries-budgets-outcome-portfolios','measurement_repository_version':'1.5.0','review_workflow':'roles-assignments-comments-quality-approvals-corrections-publications','review_workflow_version':'1.6.0','analysis_repository':'trends-comparisons-scenarios-uncertainty','analysis_repository_version':'1.7.0'}
