from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php').read_text()
JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js').read_text()
WORKSPACE_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-workspace.js').read_text()
EVIDENCE_JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-evidence.js').read_text()
EVIDENCE_CSS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-evidence.css').read_text()

def test_plugin_version_shortcodes_and_instance_ids():
    assert '* Version: 1.3.0' in PHP
    assert "define('GIC_DEMO_VERSION', '1.3.0')" in PHP
    assert "add_shortcode('global_impact_catalyst_demo'" in PHP
    assert "add_shortcode('global_impact_catalyst_workspace'" in PHP
    assert "add_shortcode('global_impact_catalyst_evidence_ledger'" in PHP
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
