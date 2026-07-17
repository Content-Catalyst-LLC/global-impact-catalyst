#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.2.0."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGE='1.2.0'; CONTRACT='1.1.0'; DATABASE=3
errors=[]
def require(condition,message):
    if not condition: errors.append(message)

manifest=json.loads((ROOT/'global_impact_catalyst_manifest.json').read_text())
require(manifest.get('version')==PACKAGE,'manifest package version mismatch')
require(manifest.get('contract_version')==CONTRACT,'manifest contract version mismatch')
require(manifest.get('schema_version')==CONTRACT,'manifest schema version mismatch')
require(manifest.get('database_schema_version')==DATABASE,'manifest database schema version mismatch')
require(manifest.get('workspace_bundle_version')==PACKAGE,'manifest workspace bundle version mismatch')
require(manifest.get('shortcode')=='[global_impact_catalyst_demo]','manifest demo shortcode mismatch')
require(manifest.get('workspace_shortcode')=='[global_impact_catalyst_workspace]','manifest workspace shortcode mismatch')
path_keys=(
 'core_path','browser_core_path','plugin_path','input_schema_path','schema_path','compatibility_schema_path',
 'validation_schema_path','fixtures_path','legacy_fixture_path','methodology_path','contract_reference_path',
 'validation_rules_path','migration_path','repository_path','service_path','repository_cli_path',
 'workspace_bundle_schema_path','database_migrations_path','persistent_repository_doc_path',
 'database_migrations_doc_path','workspace_bundles_doc_path','wordpress_workspace_doc_path'
)
for key in path_keys:
    require(key in manifest,f'manifest key missing: {key}')
    if key in manifest: require((ROOT/manifest[key]).exists(),f'manifest path missing: {key} -> {manifest[key]}')
require(len(manifest.get('repository_capabilities',[]))>=12,'repository capability registry incomplete')

core=(ROOT/'python/global_impact_core.py').read_text()
for needle in (f'ENGINE_VERSION = "{CONTRACT}"',f'CONTRACT_VERSION = "{CONTRACT}"','def build_impact_contract','def migrate_legacy_record'):
    require(needle in core,f'Python contract engine missing: {needle}')
repository=(ROOT/'python/global_impact_repository.py').read_text()
for needle in (f'DATABASE_SCHEMA_VERSION = {DATABASE}','class SQLiteImpactRepository','class OptimisticConcurrencyError','def save_contract','def autosave_contract','def record_import','def export_workspace_bundle','def restore_workspace_bundle','def backup_database'):
    require(needle in repository,f'repository contract missing: {needle}')
service=(ROOT/'python/global_impact_service.py').read_text()
for needle in (f'SERVICE_VERSION = "{PACKAGE}"','class ImpactApplicationService','def create_initiative','def duplicate_initiative','def import_document'):
    require(needle in service,f'application service missing: {needle}')
app=(ROOT/'app/main.py').read_text()
for needle in ("'version': \"1.2.0\"" if False else '"version": "1.2.0"',):
    pass
require('"version": "1.2.0"' in app,'application health package version mismatch')
require('"contract_version": "1.1.0"' in app,'application health contract version mismatch')
require('"database_schema_version": 3' in app,'application database schema version mismatch')

js=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js').read_text()
for needle in (f"const ENGINE_VERSION = '{CONTRACT}'",f"const CONTRACT_VERSION = '{CONTRACT}'",'buildImpactContract: buildImpactContract','formInput: formInput'):
    require(needle in js,f'browser contract engine missing: {needle}')
workspace_js=(ROOT/'wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-workspace.js').read_text()
for needle in ('refreshList','saveContract','autosave','openRecord','expected_revision','data-gic-workspace-import'):
    require(needle in workspace_js,f'workspace client missing: {needle}')

plugin=(ROOT/'wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php').read_text()
header=re.search(r'^ \* Version:\s*([^\s]+)',plugin,re.MULTILINE)
constant=re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)",plugin)
require(bool(header) and header.group(1)==PACKAGE,'WordPress plugin header version mismatch')
require(bool(constant) and constant.group(1)==PACKAGE,'WordPress plugin constant version mismatch')
for needle in ("add_shortcode('global_impact_catalyst_demo'","add_shortcode('global_impact_catalyst_workspace'",'gic_repository_activate','gic_revision_conflict',"register_rest_route('global-impact-catalyst/v1'"):
    require(needle in plugin,f'WordPress persistence contract missing: {needle}')

for name in ('global_impact_input.schema.json','global_impact_contract.schema.json','global_impact_record.schema.json','global_impact_validation_result.schema.json'):
    schema=json.loads((ROOT/'schemas'/name).read_text())
    require(schema.get('x-global-impact-catalyst-version')==CONTRACT,f'canonical schema version mismatch: {name}')
    require(f'/{CONTRACT}/' in schema.get('$id',''),f'canonical schema ID not versioned: {name}')
bundle_schema=json.loads((ROOT/'schemas/global_impact_workspace_bundle.schema.json').read_text())
require(bundle_schema.get('x-global-impact-catalyst-version')==PACKAGE,'workspace bundle schema version mismatch')
require(f'/{PACKAGE}/' in bundle_schema.get('$id',''),'workspace bundle schema ID mismatch')

fixtures=sorted((ROOT/'contracts/fixtures').glob('*.json'))
require(len(fixtures)>=15,'canonical fixture suite must contain at least 15 fixtures')
for path in fixtures:
    fixture=json.loads(path.read_text())
    require(fixture.get('expected',{}).get('contract_version')==CONTRACT,f'fixture contract version mismatch: {path.name}')

migration_files=sorted((ROOT/'migrations').glob('*.sql'))
require([path.name for path in migration_files]==['001_core_repository.sql','002_portfolios_and_autosave.sql','003_imports_audit_and_bundles.sql'],'database migration inventory mismatch')

changelog=(ROOT/'CHANGELOG.md').read_text()
require('## [1.2.0]' in changelog,'CHANGELOG missing v1.2.0')
require((ROOT/'release/v1.2.0.md').exists(),'v1.2.0 release notes missing')
readme=(ROOT/'README.md').read_text()
for needle in ('Persistent Initiatives','Optimistic concurrency','Workspace export','[global_impact_catalyst_workspace]'):
    require(needle in readme,f'README section missing: {needle}')
for doc in ('docs/persistent-repository.md','docs/database-migrations.md','docs/workspace-bundles.md','docs/wordpress-workspace.md'):
    require((ROOT/doc).stat().st_size>500,f'document incomplete: {doc}')

if errors:
    for error in errors: print(f'ERROR: {error}',file=sys.stderr)
    raise SystemExit(1)
print('Global Impact Catalyst v1.2.0 release contract passed.')
