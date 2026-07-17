#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.1.0."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='1.1.0'
errors=[]
def require(condition,message):
    if not condition: errors.append(message)

manifest=json.loads((ROOT/'global_impact_catalyst_manifest.json').read_text())
for key in ('version','contract_version','schema_version'):
    require(manifest.get(key)==EXPECTED,f'manifest {key} mismatch')
require(manifest.get('shortcode')=='[global_impact_catalyst_demo]','manifest shortcode mismatch')
path_keys=('core_path','browser_core_path','plugin_path','input_schema_path','schema_path','compatibility_schema_path','validation_schema_path','fixtures_path','legacy_fixture_path','methodology_path','contract_reference_path','validation_rules_path','migration_path')
for key in path_keys:
    require(key in manifest,f'manifest key missing: {key}')
    if key in manifest: require((ROOT/manifest[key]).exists(),f'manifest path missing: {key} -> {manifest[key]}')
require(len(manifest.get('core_entities',[]))>=19,'manifest core entity registry incomplete')
require(len(manifest.get('claim_types',[]))==5,'manifest claim type registry mismatch')

core=(ROOT/'python/global_impact_core.py').read_text()
for needle in (f'ENGINE_VERSION = "{EXPECTED}"',f'CONTRACT_VERSION = "{EXPECTED}"','def build_impact_contract','def validate_input','def migrate_legacy_record','def stable_id'):
    require(needle in core,f'Python core missing: {needle}')
js=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js').read_text()
for needle in (f"const ENGINE_VERSION = '{EXPECTED}'",f"const CONTRACT_VERSION = '{EXPECTED}'",'buildImpactContract: buildImpactContract','validateInput: validateInput'):
    require(needle in js,f'Browser core missing: {needle}')

plugin=(ROOT/'wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php').read_text()
header=re.search(r'^ \* Version:\s*([^\s]+)',plugin,re.MULTILINE)
constant=re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)",plugin)
require(bool(header) and header.group(1)==EXPECTED,'WordPress plugin header version mismatch')
require(bool(constant) and constant.group(1)==EXPECTED,'WordPress plugin constant version mismatch')
require("add_shortcode('global_impact_catalyst_demo'" in plugin,'WordPress shortcode registration missing')
require('static $instance = 0' in plugin and '$id_prefix' in plugin,'per-instance shortcode IDs missing')
for field in ('workspace','outcome','indicatorDefinition','targetPeriod','sourceLocator','designType','claimType','claimStatement'):
    require(f'name="{field}"' in plugin,f'WordPress canonical field missing: {field}')

schema_ids=[]
for name in ('global_impact_input.schema.json','global_impact_contract.schema.json','global_impact_record.schema.json','global_impact_validation_result.schema.json'):
    schema=json.loads((ROOT/'schemas'/name).read_text())
    require(schema.get('x-global-impact-catalyst-version')==EXPECTED,f'schema version mismatch: {name}')
    require(f'/{EXPECTED}/' in schema.get('$id',''),f'schema ID not versioned: {name}')
    schema_ids.append(schema.get('$id'))
require(len(set(schema_ids))==len(schema_ids),'schema IDs must be unique')
contract_schema=json.loads((ROOT/'schemas/global_impact_contract.schema.json').read_text())
for key in ('facts','derived','governance','validation','provenance'):
    require(key in contract_schema.get('properties',{}),f'contract schema root missing {key}')

fixtures=sorted((ROOT/'contracts/fixtures').glob('*.json'))
require(len(fixtures)>=15,'canonical fixture suite must contain at least 15 fixtures')
for path in fixtures:
    fixture=json.loads(path.read_text())
    require(fixture.get('expected',{}).get('contract_version')==EXPECTED,f'fixture contract version mismatch: {path.name}')
    require('validation' in fixture.get('expected',{}),f'fixture validation missing: {path.name}')
legacy=json.loads((ROOT/'contracts/legacy/legacy-v1.0.1-record.json').read_text())
require(legacy.get('record_type')=='global_impact_catalyst_record','legacy migration fixture is not a v1.0.x flat record')

changelog=(ROOT/'CHANGELOG.md').read_text()
require('## [1.1.0]' in changelog,'CHANGELOG missing v1.1.0')
require((ROOT/'release/v1.1.0.md').exists(),'v1.1.0 release notes missing')
readme=(ROOT/'README.md').read_text()
for needle in ('Canonical Impact Contract','Lossless migration','Claim governance','Cross-runtime parity'):
    require(needle in readme,f'README section missing: {needle}')
for doc in ('docs/canonical-impact-contract.md','docs/validation-rules.md','docs/claim-governance.md','docs/migration-v1.0-to-v1.1.md'):
    require((ROOT/doc).stat().st_size>400,f'document incomplete: {doc}')

if errors:
    for error in errors: print(f'ERROR: {error}',file=sys.stderr)
    raise SystemExit(1)
print('Global Impact Catalyst v1.1.0 release contract passed.')
