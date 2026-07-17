#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.3.0."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKAGE='1.3.0'; CONTRACT='1.1.0'; DATABASE=4
errors=[]
def require(condition,message):
    if not condition: errors.append(message)

def read(path): return (ROOT/path).read_text(encoding='utf-8')
manifest=json.loads(read('global_impact_catalyst_manifest.json'))
for key,value in (
    ('version',PACKAGE),('contract_version',CONTRACT),('schema_version',CONTRACT),
    ('database_schema_version',DATABASE),('workspace_bundle_version',PACKAGE),('evidence_chain_version',PACKAGE),
    ('shortcode','[global_impact_catalyst_demo]'),('workspace_shortcode','[global_impact_catalyst_workspace]'),
    ('evidence_shortcode','[global_impact_catalyst_evidence_ledger]')):
    require(manifest.get(key)==value,f'manifest {key} mismatch')
path_keys=(
 'core_path','browser_core_path','plugin_path','input_schema_path','schema_path','compatibility_schema_path',
 'validation_schema_path','fixtures_path','legacy_fixture_path','methodology_path','contract_reference_path',
 'validation_rules_path','migration_path','repository_path','service_path','repository_cli_path',
 'workspace_bundle_schema_path','database_migrations_path','persistent_repository_doc_path',
 'database_migrations_doc_path','workspace_bundles_doc_path','wordpress_workspace_doc_path',
 'evidence_chain_schema_path','evidence_repository_schema_path','evidence_repository_doc_path',
 'evidence_chain_doc_path','source_integrity_doc_path','evidence_chain_example_path','evidence_repository_example_path')
for key in path_keys:
    require(key in manifest,f'manifest key missing: {key}')
    if key in manifest: require((ROOT/manifest[key]).exists(),f'manifest path missing: {key} -> {manifest[key]}')
required_caps={
 'sqlite','migrations','entity_crud','optimistic_concurrency','workspace_bundle','database_backup',
 'source_registry','source_versions','sha256_integrity','evidence_capture','dataset_registry',
 'provenance_graph','claim_evidence_links','contradiction_visibility','evidence_chain_export'}
require(required_caps.issubset(set(manifest.get('repository_capabilities',[]))),'repository capability registry incomplete')

core=read('python/global_impact_core.py')
for needle in (f'ENGINE_VERSION = "{CONTRACT}"',f'CONTRACT_VERSION = "{CONTRACT}"','def build_impact_contract','def migrate_legacy_record'):
    require(needle in core,f'Python contract engine missing: {needle}')
repository=read('python/global_impact_repository.py')
for needle in (
    f'DATABASE_SCHEMA_VERSION = {DATABASE}','class SQLiteImpactRepository','class OptimisticConcurrencyError',
    'def save_contract','def export_workspace_bundle','def restore_workspace_bundle','def backup_database',
    'def register_source','def add_source_version','def capture_evidence','def register_dataset',
    'def add_provenance_edge','def link_claim_evidence','def evidence_chain','def export_evidence_repository',
    'EVIDENCE_TYPES','CLAIM_EVIDENCE_RELATIONSHIPS','CHECKSUM_ALGORITHMS'):
    require(needle in repository,f'repository contract missing: {needle}')
service=read('python/global_impact_service.py')
for needle in (f'SERVICE_VERSION = "{PACKAGE}"','class ImpactApplicationService','def register_source','def add_source_version','def capture_evidence','def register_dataset','def link_claim_evidence','def evidence_chain'):
    require(needle in service,f'application service missing: {needle}')
app=read('app/main.py')
for needle,message in ((f'"version": "{PACKAGE}"','application health package version mismatch'),(f'"contract_version": "{CONTRACT}"','application health contract version mismatch'),(f'"database_schema_version": {DATABASE}','application database schema version mismatch'),('"evidence_repository": "sources-provenance-evidence"','application evidence repository marker missing')):
    require(needle in app,message)

js=read('wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js')
for needle in (f"const ENGINE_VERSION = '{CONTRACT}'",f"const CONTRACT_VERSION = '{CONTRACT}'",'buildImpactContract: buildImpactContract','formInput: formInput'):
    require(needle in js,f'browser contract engine missing: {needle}')
workspace_js=read('wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-workspace.js')
for needle in ('refreshList','saveContract','autosave','expected_revision','data-gic-workspace-import'):
    require(needle in workspace_js,f'workspace client missing: {needle}')
evidence_js=read('wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-evidence.js')
for needle in ('data-gic-evidence-ledger','data-gic-source-form','data-gic-evidence-form','data-gic-dataset-form','data-gic-claim-link-form','evidence-chain/'):
    require(needle in evidence_js,f'evidence client missing: {needle}')

plugin=read('wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
header=re.search(r'^ \* Version:\s*([^\s]+)',plugin,re.MULTILINE)
constant=re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)",plugin)
require(bool(header) and header.group(1)==PACKAGE,'WordPress plugin header version mismatch')
require(bool(constant) and constant.group(1)==PACKAGE,'WordPress plugin constant version mismatch')
for needle in (
    "add_shortcode('global_impact_catalyst_demo'","add_shortcode('global_impact_catalyst_workspace'",
    "add_shortcode('global_impact_catalyst_evidence_ledger'",'gic_evidence_materialize_contract',
    'gic_evidence_source_upsert','gic_evidence_capture_rest','gic_evidence_dataset_rest','gic_evidence_link_rest',
    'gic_evidence_chain_rest',"'/evidence-chain/(?P<initiative_id>","gic_repository_table('source_versions')",
    "gic_repository_table('claim_evidence')"):
    require(needle in plugin,f'WordPress evidence contract missing: {needle}')

for name in ('global_impact_input.schema.json','global_impact_contract.schema.json','global_impact_record.schema.json','global_impact_validation_result.schema.json'):
    schema=json.loads(read('schemas/'+name))
    require(schema.get('x-global-impact-catalyst-version')==CONTRACT,f'canonical schema version mismatch: {name}')
    require(f'/{CONTRACT}/' in schema.get('$id',''),f'canonical schema ID not versioned: {name}')
for name in ('global_impact_workspace_bundle.schema.json','global_impact_evidence_chain.schema.json','global_impact_evidence_repository.schema.json'):
    schema=json.loads(read('schemas/'+name))
    require(schema.get('x-global-impact-catalyst-version')==PACKAGE,f'v1.3 schema version mismatch: {name}')
    require(f'/{PACKAGE}/' in schema.get('$id',''),f'v1.3 schema ID mismatch: {name}')

fixtures=sorted((ROOT/'contracts/fixtures').glob('*.json'))
require(len(fixtures)>=15,'canonical fixture suite must contain at least 15 fixtures')
for path in fixtures:
    fixture=json.loads(path.read_text())
    require(fixture.get('expected',{}).get('contract_version')==CONTRACT,f'fixture contract version mismatch: {path.name}')
migration_names=[p.name for p in sorted((ROOT/'migrations').glob('*.sql'))]
require(migration_names==['001_core_repository.sql','002_portfolios_and_autosave.sql','003_imports_audit_and_bundles.sql','004_sources_provenance_evidence.sql'],'database migration inventory mismatch')

changelog=read('CHANGELOG.md')
require('## [1.3.0]' in changelog,'CHANGELOG missing v1.3.0')
require((ROOT/'release/v1.3.0.md').exists(),'v1.3.0 release notes missing')
readme=read('README.md')
for needle in ('Sources, Provenance, and Evidence Chain','SHA-256','evidence ledger','[global_impact_catalyst_evidence_ledger]'):
    require(needle in readme,f'README section missing: {needle}')
for doc in ('docs/sources-provenance-evidence.md','docs/evidence-chain.md','docs/source-integrity.md','docs/persistent-repository.md','docs/database-migrations.md','docs/workspace-bundles.md','docs/wordpress-workspace.md'):
    require((ROOT/doc).stat().st_size>500,f'document incomplete: {doc}')
for example in ('examples/example_global_impact_evidence_chain.json','examples/example_global_impact_evidence_repository.json','examples/example_global_impact_workspace_bundle.json'):
    require((ROOT/example).stat().st_size>100,f'example incomplete: {example}')

if errors:
    for error in errors: print(f'ERROR: {error}',file=sys.stderr)
    raise SystemExit(1)
print('Global Impact Catalyst v1.3.0 release contract passed.')
