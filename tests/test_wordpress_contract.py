from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php').read_text()
JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js').read_text()
WORKSPACE_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-workspace.js').read_text()
EVIDENCE_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-evidence.js').read_text()
EVIDENCE_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-evidence.css').read_text()
REGISTRY_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-registry.js').read_text()
REGISTRY_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-registry.css').read_text()
MEASUREMENT_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-measurement.js').read_text()
MEASUREMENT_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-measurement.css').read_text()

def test_plugin_version_shortcodes_and_instance_ids():
    assert '* Version: 1.5.0' in PHP
    assert "define('GIC_DEMO_VERSION', '1.5.0')" in PHP
    assert "add_shortcode('global_impact_catalyst_demo'" in PHP
    assert "add_shortcode('global_impact_catalyst_workspace'" in PHP
    assert "add_shortcode('global_impact_catalyst_evidence_ledger'" in PHP
    assert "add_shortcode('global_impact_catalyst_indicator_registry'" in PHP
    assert "add_shortcode('global_impact_catalyst_measurement_portfolio'" in PHP
    assert 'static $instance = 0' in PHP and '$id_prefix' in PHP

def test_plugin_exposes_contract_and_claim_fields():
    for field in ['workspace','outcome','indicatorDefinition','targetPeriod','sourceLocator','designType','claimType','claimStatement']:
        assert f'name="{field}"' in PHP

def test_browser_exports_canonical_contract_api_without_contract_drift():
    assert "ENGINE_VERSION = '1.1.0'" in JS
    assert "CONTRACT_VERSION = '1.1.0'" in JS
    for api in ['buildImpactContract: buildImpactContract','validateInput: validateInput','formInput: formInput','render: render']:
        assert api in JS
    assert "contract_type: 'global_impact_contract'" in JS

def test_wordpress_persistence_tables_rest_and_conflict_contract():
    for table in ["gic_repository_table('contracts')","gic_repository_table('autosaves')","gic_repository_table('audit')"]:
        assert table in PHP
    for behavior in ['gic_repository_activate','gic_repository_save_contract','gic_repository_autosave_contract','gic_repository_list_contracts','gic_repository_change_archive']:
        assert f'function {behavior}' in PHP
    assert 'gic_revision_conflict' in PHP and "'status' => 409" in PHP
    assert "register_rest_route('global-impact-catalyst/v1'" in PHP

def test_workspace_client_supports_repository_operations():
    for operation in ['refreshList','saveContract','autosave','openRecord','data-gic-workspace-duplicate','data-gic-workspace-archive','data-gic-workspace-import']:
        assert operation in WORKSPACE_JS or operation in PHP

def test_evidence_tables_materialization_routes_and_shortcode_are_present():
    for table in ['sources','source_versions','evidence','datasets','provenance','claim_evidence']:
        assert f"gic_repository_table('{table}')" in PHP
    for behavior in ['gic_evidence_materialize_contract','gic_evidence_source_upsert','gic_evidence_capture_rest','gic_evidence_dataset_rest','gic_evidence_link_rest','gic_evidence_chain_rest']:
        assert f'function {behavior}' in PHP
    for route in ['/sources','/evidence','/datasets','/claim-evidence','/evidence-chain/']:
        assert route in PHP
    for control in ['data-gic-evidence-ledger','data-gic-source-form','data-gic-evidence-form','data-gic-dataset-form','data-gic-claim-link-form']:
        assert control in PHP

def test_evidence_client_and_styles_support_chain_operations():
    for operation in ['evidence-chain/','claim-evidence','data-gic-evidence-download','contradicting_link_count']:
        assert operation in EVIDENCE_JS or operation in PHP
    assert '.gic-evidence__grid' in EVIDENCE_CSS and '@media' in EVIDENCE_CSS


def test_indicator_registry_tables_routes_materialization_and_shortcode_are_present():
    for table in ['units','indicator_definitions','indicator_versions','baseline_models','baseline_versions','target_models','target_versions','method_definitions','method_versions','indicator_bindings']:
        assert f"gic_repository_table('{table}')" in PHP
    for behavior in ['gic_registry_seed_units','gic_registry_materialize_contract','gic_registry_store_version','gic_registry_export','gic_registry_unit_rest','gic_registry_definition_rest','gic_registry_model_rest','gic_registry_method_rest']:
        assert f'function {behavior}' in PHP
    for route in ['/indicator-registry','/units','/indicator-definitions','/baseline-models','/target-models','/method-definitions']:
        assert route in PHP
    for control in ['data-gic-indicator-registry','data-gic-registry-workspace','data-gic-unit-form','data-gic-indicator-form','data-gic-baseline-form','data-gic-target-form','data-gic-method-form']:
        assert control in PHP


def test_indicator_registry_client_and_styles_support_governed_records():
    for operation in ['indicator-registry?workspace_id=','baseline-models','target-models','method-definitions','data-gic-registry-download']:
        assert operation in REGISTRY_JS or operation in PHP
    assert '.gic-registry__grid' in REGISTRY_CSS and '@media' in REGISTRY_CSS


def test_measurement_tables_routes_and_shortcode_are_present():
    for table in ['impact_results','result_relationships','observation_series','beneficiary_definitions','beneficiary_observations','financial_records','external_factors','contribution_notes','outcome_portfolios','outcome_portfolio_members','portfolio_aggregation_runs']:
        assert f"gic_repository_table('{table}')" in PHP
    for route in ['/measurement-repository','/observations','/beneficiary-definitions','/beneficiary-observations','/financial-records','/outcome-portfolios','/outcome-portfolio-members']:
        assert route in PHP
    for control in ['data-gic-measurement-portfolio','data-gic-observation-form','data-gic-beneficiary-form','data-gic-beneficiary-observation-form','data-gic-financial-form','data-gic-outcome-portfolio-form']:
        assert control in PHP


def test_measurement_client_and_styles_support_program_records():
    for operation in ['measurement-repository?workspace_id=','beneficiary-definitions','beneficiary-observations','financial-records','outcome-portfolios','data-gic-measurement-download']:
        assert operation in MEASUREMENT_JS or operation in PHP
    assert '.gic-measurement__grid' in MEASUREMENT_CSS and '@media' in MEASUREMENT_CSS
