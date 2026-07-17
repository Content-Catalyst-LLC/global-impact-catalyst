#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.9.0."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
PACKAGE='1.9.0'; CONTRACT='1.1.0'; DATABASE=10
VERSIONS={'evidence_chain_version':'1.3.0','indicator_registry_version':'1.4.0','measurement_repository_version':'1.5.0','review_workflow_version':'1.6.0','analysis_repository_version':'1.7.0','reporting_repository_version':'1.8.0','integration_repository_version':'1.9.0'}
errors=[]
def require(ok,msg):
    if not ok: errors.append(msg)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))

manifest=load('global_impact_catalyst_manifest.json')
for key,expected in {'version':PACKAGE,'contract_version':CONTRACT,'schema_version':CONTRACT,'database_schema_version':DATABASE,'workspace_bundle_version':PACKAGE,'api_version':'v1',**VERSIONS}.items():
    require(manifest.get(key)==expected,f'manifest {key} mismatch: {manifest.get(key)!r}')
for key in [
 'core_path','repository_path','service_path','repository_cli_path','workspace_bundle_schema_path',
 'integration_module_path','integration_repository_schema_path','public_api_schema_path','embed_schema_path','platform_handoff_schema_path',
 'public_api_doc_path','embeds_doc_path','platform_handoffs_doc_path','jsonld_doc_path',
 'integration_repository_example_path','public_api_example_path','platform_handoff_example_path','database_migration_10']:
    value=manifest.get(key); require(bool(value) and (ROOT/value).exists(),f'manifest path missing: {key} -> {value}')
required_caps={
 'api_client_registry','one_time_api_key_issuance','sha256_api_key_storage','scoped_api_access','api_key_revocation',
 'fixed_window_rate_limits','idempotency_records','api_access_audit','privacy_safe_public_catalog','approved_publication_api',
 'workspace_api_pagination','jsonld_interoperability','governed_embeds','public_embed_rendering','publication_snapshot_embed_binding',
 'sustainable_catalyst_handoffs','checksum_bound_handoffs','idempotent_handoff_creation','handoff_delivery_receipts',
 'integration_event_ledger','integration_repository_export','lossless_integration_restore','wordpress_integration_hub','wordpress_public_embeds'}
require(required_caps.issubset(set(manifest.get('repository_capabilities',[]))),'integration capabilities incomplete')

repo=read('python/global_impact_repository.py')
for marker in ['DATABASE_SCHEMA_VERSION = 10','PublicAPIIntegrationMixin','010_public_api_embeds_platform_handoffs.sql','"bundle_version": "1.9.0"','"integration_repository": self.export_integration_repository(workspace_id)','self._restore_integration_repository','"api_clients": count("api_clients")','"platform_handoffs": count("platform_handoffs")']:
    require(marker in repo,f'repository contract missing: {marker}')
integration=read('python/global_impact_integration.py')
for marker in ['INTEGRATION_VERSION = "1.9.0"','API_VERSION = "v1"','def register_api_client','def issue_api_key','def authenticate_api_key','def idempotent_operation','def public_catalog','def public_publication','def workspace_api_resource','def create_embed','def render_embed','def create_platform_handoff','def record_handoff_delivery','def export_integration_repository','def _restore_integration_repository','api_key_material_exported']:
    require(marker in integration,f'integration contract missing: {marker}')
for destination in ['catalyst_data','catalyst_analytics_r','site_intelligence','workbench','research_lab','knowledge_library','research_librarian','decision_studio','platform_core','advisory']:
    require(destination in integration,f'handoff destination missing: {destination}')
service=read('python/global_impact_service.py')
for marker in ['SERVICE_VERSION = "1.9.0"','def register_api_client','def issue_api_key','def public_catalog','def public_publication','def workspace_api_resource','def create_embed','def render_embed','def create_platform_handoff','def integration_repository']:
    require(marker in service,f'service contract missing: {marker}')
app=read('app/main.py')
for marker in ['"version": "1.9.0"','"database_schema_version": 10','"integration_repository_version": "1.9.0"','"api_version": "v1"']:
    require(marker in app,f'application contract missing: {marker}')
cli=read('scripts/gic_repository.py')
for command in ['add-api-client','issue-api-key','public-catalog','public-publication','workspace-api','add-embed','render-embed','platform-handoff','platform-handoffs','integration-repository']:
    require(f"'{command}'" in cli or f'"{command}"' in cli,f'CLI command missing: {command}')

php=read('wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
for marker in ['* Version: 1.9.0',"define('GIC_DEMO_VERSION', '1.9.0')","update_option('gic_repository_schema_version', 10, false)","add_shortcode('global_impact_catalyst_integration_hub'","add_shortcode('global_impact_catalyst_public_profile'","add_shortcode('global_impact_catalyst_indicator_view'","add_shortcode('global_impact_catalyst_report_view'","add_shortcode('global_impact_catalyst_compact_embed'",'/public/initiatives','/public/publications/','/public/embeds/','/api-clients','/platform-handoffs','/integration-repository']:
    require(marker in php,f'WordPress integration contract missing: {marker}')
for table in ['api_clients','api_keys','api_access_log','embed_definitions','platform_handoffs','integration_events']:
    require(f"gic_repository_table('{table}')" in php,f'WordPress table missing: {table}')
for asset in ['global-impact-catalyst-integration.js','global-impact-catalyst-integration.css']:
    require((ROOT/'wordpress/global-impact-catalyst-demo/assets'/asset).exists(),f'WordPress asset missing: {asset}')

schema_examples={
 'global_impact_public_api_response.schema.json':'example_global_impact_public_api_response.json',
 'global_impact_platform_handoff.schema.json':'example_global_impact_platform_handoff.json',
 'global_impact_integration_repository.schema.json':'example_global_impact_integration_repository.json',
 'global_impact_workspace_bundle.schema.json':'example_global_impact_workspace_bundle.json'}
for schema_name,example_name in schema_examples.items():
    schema=load('schemas/'+schema_name); example=load('examples/'+example_name)
    require(schema.get('x-global-impact-catalyst-version')==PACKAGE or schema_name=='global_impact_workspace_bundle.schema.json',f'{schema_name} version marker missing')
    for err in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(example): errors.append(f'{example_name}: {err.message}')
serialized=json.dumps(load('examples/example_global_impact_integration_repository.json'))
require('gic_live_' not in serialized and 'key_hash' not in serialized,'integration example exposes API key material')

migration=read('migrations/010_public_api_embeds_platform_handoffs.sql')
for table in ['api_clients','api_keys','api_idempotency_records','api_rate_windows','api_access_log','embed_definitions','platform_handoffs','integration_events']:
    require(re.search(rf'CREATE TABLE IF NOT EXISTS\s+{table}\b',migration,re.I) is not None,f'migration 10 table missing: {table}')
for path in ['README.md','CHANGELOG.md','release/v1.9.0.md','docs/public-api.md','docs/embeds.md','docs/sustainable-catalyst-handoffs.md','docs/jsonld-interoperability.md']:
    require('1.9.0' in read(path) or path.startswith('docs/'),f'v1.9.0 documentation marker missing: {path}')
require('Public API, Embeds, and Sustainable Catalyst Handoffs' in read('README.md'),'README release title missing')

if errors:
    print('Global Impact Catalyst v1.9.0 release contract FAILED:',file=sys.stderr)
    for error in errors: print(f'- {error}',file=sys.stderr)
    raise SystemExit(1)
print('Global Impact Catalyst v1.9.0 release contract passed.')
