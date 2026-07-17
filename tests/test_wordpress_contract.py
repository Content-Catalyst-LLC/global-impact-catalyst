from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PHP=(ROOT/'wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php').read_text()
JS=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js').read_text()

def test_plugin_version_shortcode_and_instance_ids():
    assert '* Version: 1.1.0' in PHP
    assert "define('GIC_DEMO_VERSION', '1.1.0')" in PHP
    assert "add_shortcode('global_impact_catalyst_demo'" in PHP
    assert 'static $instance = 0' in PHP and '$id_prefix' in PHP

def test_plugin_exposes_contract_and_claim_fields():
    for field in ['workspace','outcome','indicatorDefinition','targetPeriod','sourceLocator','designType','claimType','claimStatement']:
        assert f'name="{field}"' in PHP

def test_browser_exports_canonical_contract_api():
    assert "CONTRACT_VERSION = '1.1.0'" in JS
    assert 'buildImpactContract: buildImpactContract' in JS
    assert 'validateInput: validateInput' in JS
    assert "contract_type: 'global_impact_contract'" in JS
