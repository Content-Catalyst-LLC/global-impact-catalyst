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
REVIEW_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-review.js').read_text()
REVIEW_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-review.css').read_text()
ANALYSIS_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-analysis.js').read_text()
ANALYSIS_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-analysis.css').read_text()
REPORTING_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-reporting.js').read_text()
REPORTING_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-reporting.css').read_text()
INTEGRATION_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-integration.js').read_text()
INTEGRATION_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-integration.css').read_text()

def test_plugin_version_shortcodes_and_instance_ids():
    assert '* Version: 1.9.0' in PHP
    assert "define('GIC_DEMO_VERSION', '1.9.0')" in PHP
    assert "add_shortcode('global_impact_catalyst_demo'" in PHP
    assert "add_shortcode('global_impact_catalyst_workspace'" in PHP
    assert "add_shortcode('global_impact_catalyst_evidence_ledger'" in PHP
    assert "add_shortcode('global_impact_catalyst_indicator_registry'" in PHP
    assert "add_shortcode('global_impact_catalyst_measurement_portfolio'" in PHP
    assert "add_shortcode('global_impact_catalyst_review_workflow'" in PHP
    assert "add_shortcode('global_impact_catalyst_analysis_studio'" in PHP
    assert "add_shortcode('global_impact_catalyst_reporting_studio'" in PHP
    assert "add_shortcode('global_impact_catalyst_integration_hub'" in PHP
    assert "add_shortcode('global_impact_catalyst_public_profile'" in PHP
    assert "add_shortcode('global_impact_catalyst_indicator_view'" in PHP
    assert "add_shortcode('global_impact_catalyst_report_view'" in PHP
    assert "add_shortcode('global_impact_catalyst_compact_embed'" in PHP
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


def test_review_workflow_tables_routes_materialization_and_shortcode_are_present():
    for table in ['workflow_roles','review_assignments','review_comments','quality_assessments','approval_decisions','workflow_revisions','correction_records','publication_records','publication_events']:
        assert f"gic_repository_table('{table}')" in PHP
    for behavior in ['gic_review_ensure_roles','gic_review_record_contract_revision','gic_review_export','gic_review_assignment_rest','gic_review_comment_rest','gic_review_quality_rest','gic_review_decision_rest','gic_review_correction_rest','gic_review_publication_rest','gic_review_publish_rest','gic_review_withdraw_rest']:
        assert f'function {behavior}' in PHP
    for route in ['/review-workflow','/review-assignments','/review-comments','/quality-assessments','/approval-decisions','/corrections','/publications']:
        assert route in PHP
    for control in ['data-gic-review','data-gic-review-load','data-gic-review-assignment','data-gic-review-assessment','data-gic-review-list']:
        assert control in PHP


def test_review_workflow_client_and_styles_support_governed_review():
    for operation in ['review-workflow?workspace_id=','review-assignments','quality-assessments','data-gic-review-count']:
        assert operation in REVIEW_JS or operation in PHP
    assert '.gic-review__grid' in REVIEW_CSS and '@media' in REVIEW_CSS


def test_analysis_tables_routes_and_shortcode_are_present():
    for table in ['analysis_benchmarks','analysis_comparison_sets','analysis_comparison_members','analysis_scenarios','analysis_uncertainty_models','analysis_runs','analysis_sensitivity_runs']:
        assert f"gic_repository_table('{table}')" in PHP
    for behavior in ['gic_analysis_repository','gic_analysis_benchmark_rest','gic_analysis_uncertainty_rest','gic_analysis_scenario_rest','gic_analysis_trend_rest','gic_analysis_comparison_set_rest','gic_analysis_sensitivity_rest']:
        assert f'function {behavior}' in PHP
    for route in ['/analysis-repository','/analysis-benchmarks','/analysis-uncertainty-models','/analysis-scenarios','/analysis-trends','/analysis-comparison-sets','/analysis-sensitivity']:
        assert route in PHP
    for control in ['data-gic-analysis-studio','data-gic-analysis-load','data-gic-analysis-trend','data-gic-analysis-benchmark','data-gic-analysis-uncertainty','data-gic-analysis-scenario','data-gic-analysis-results']:
        assert control in PHP

def test_analysis_client_and_styles_support_analytical_operations():
    for operation in ['analysis-repository?workspace_id=','analysis-trends','analysis-benchmarks','analysis-uncertainty-models','analysis-scenarios']:
        assert operation in ANALYSIS_JS or operation in PHP
    assert '.gic-analysis__grid' in ANALYSIS_CSS and '@media' in ANALYSIS_CSS


def test_reporting_tables_routes_and_shortcode_are_present():
    for table in ['report_templates','report_documents','dashboard_definitions','dashboard_cards','publication_snapshots','export_bundles','export_artifacts']:
        assert f"gic_repository_table('{table}')" in PHP
    for behavior in ['gic_reporting_repository_rest','gic_reporting_template_rest','gic_reporting_report_rest','gic_reporting_dashboard_rest','gic_reporting_snapshot_rest','gic_reporting_export_rest','gic_reporting_register_routes','gic_reporting_studio_shortcode']:
        assert f'function {behavior}' in PHP
    for route in ['/reporting-repository','/report-templates','/reports','/dashboards','/publication-snapshots','/reproducible-exports']:
        assert route in PHP
    for control in ['data-gic-reporting-studio','data-gic-reporting-load','data-gic-reporting-template','data-gic-reporting-report','data-gic-reporting-dashboard','data-gic-reporting-snapshot','data-gic-reporting-export','data-gic-reporting-results']:
        assert control in PHP

def test_reporting_client_and_styles_support_accessible_publication_operations():
    for operation in ['reporting-repository?workspace_id=','report-templates','reports','dashboards','publication-snapshots','reproducible-exports','data-gic-reporting-results']:
        assert operation in REPORTING_JS or operation in PHP
    assert '.gic-reporting__grid' in REPORTING_CSS and '@media' in REPORTING_CSS


def test_integration_tables_routes_shortcodes_and_assets_are_present():
    for table in ['api_clients','api_keys','api_access_log','embed_definitions','platform_handoffs','integration_events']:
        assert f"gic_repository_table('{table}')" in PHP
    for behavior in ['gic_integration_public_profile','gic_integration_api_key_auth','gic_integration_workspace_resource_rest','gic_integration_api_client_rest','gic_integration_embed_rest','gic_integration_handoff_rest','gic_integration_repository_rest','gic_integration_register_routes','gic_integration_hub_shortcode']:
        assert f'function {behavior}' in PHP
    for route in ['/public/initiatives','/public/publications/','/public/embeds/','/workspace/','/api-clients','/embeds','/platform-handoffs','/integration-repository']:
        assert route in PHP
    for control in ['data-gic-integration-hub','data-gic-integration-load','data-gic-integration-client','data-gic-integration-embed','data-gic-integration-handoff','data-gic-integration-results']:
        assert control in PHP
    assert 'Connected platform service · v1.9.0' in PHP


def test_integration_client_and_styles_support_scoped_operations():
    for operation in ['integration-repository?workspace_id=','api-clients','embeds','platform-handoffs','data-gic-integration-results']:
        assert operation in INTEGRATION_JS or operation in PHP
    assert '.gic-integration__grid' in INTEGRATION_CSS and '@media' in INTEGRATION_CSS
