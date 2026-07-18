#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.10.0."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
PACKAGE='1.10.0'; CONTRACT='1.1.0'; DATABASE=11
VERSIONS={
    'evidence_chain_version':'1.3.0','indicator_registry_version':'1.4.0',
    'measurement_repository_version':'1.5.0','review_workflow_version':'1.6.0',
    'analysis_repository_version':'1.7.0','reporting_repository_version':'1.8.0',
    'integration_repository_version':'1.9.0','production_repository_version':'1.10.0'
}
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
 'production_module_path','production_repository_schema_path','production_repository_example_path',
 'production_doc_path','offline_doc_path','localization_doc_path','security_recovery_doc_path','database_migration_11']:
    value=manifest.get(key); require(bool(value) and (ROOT/value).exists(),f'manifest path missing: {key} -> {value}')
required_caps={
 'locale_registry','translation_fallbacks','right_to_left_locales','offline_package_generation','offline_source_hashes',
 'offline_change_queue','optimistic_offline_sync','revision_conflict_records','wcag_2_2_audit_records',
 'security_policy_registry','backup_plan_registry','verified_sqlite_backups','recovery_test_evidence',
 'deployment_environment_registry','release_readiness_matrix','production_blocking_gates',
 'production_repository_export','lossless_production_restore','wordpress_production_readiness'}
require(required_caps.issubset(set(manifest.get('repository_capabilities',[]))),'production capabilities incomplete')

repo=read('python/global_impact_repository.py')
for marker in ['DATABASE_SCHEMA_VERSION = 11','ProductionHardeningMixin','011_accessibility_offline_localization_production_hardening.sql','"bundle_version": "1.10.0"','"production_repository": self.export_production_repository(workspace_id)','self._restore_production_repository','"locales": count("locale_definitions")','"release_readiness_checks": count("release_readiness_checks")']:
    require(marker in repo,f'repository contract missing: {marker}')
production=read('python/global_impact_production.py')
for marker in ['PRODUCTION_VERSION = "1.10.0"','OFFLINE_PACKAGE_VERSION = "1.10.0"','def register_locale','def translate','def create_offline_package','def queue_offline_change','def apply_offline_change','def record_accessibility_audit','def set_security_policy','def create_backup_plan','def run_backup','def verify_recovery','def register_deployment_environment','def evaluate_release_readiness','def export_production_repository','def _restore_production_repository']:
    require(marker in production,f'production contract missing: {marker}')
service=read('python/global_impact_service.py')
for marker in ['SERVICE_VERSION = "1.10.0"','def register_locale','def create_offline_package','def queue_offline_change','def apply_offline_change','def record_accessibility_audit','def set_security_policy','def create_backup_plan','def register_deployment_environment','def production_repository']:
    require(marker in service,f'service contract missing: {marker}')
app=read('app/main.py')
for marker in ['"version": "1.10.0"','"database_schema_version": 11','"production_repository_version": "1.10.0"','"integration_repository_version": "1.9.0"']:
    require(marker in app,f'application contract missing: {marker}')
cli=read('scripts/gic_repository.py')
for command in ['production-repository','add-locale','offline-package','queue-offline-change','apply-offline-change','accessibility-audit','security-policy','backup-plan','run-backup','verify-recovery','add-environment','release-readiness']:
    require(f"'{command}'" in cli or f'"{command}"' in cli,f'CLI command missing: {command}')

php=read('wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
for marker in ['* Version: 1.10.0',"define('GIC_DEMO_VERSION', '1.10.0')","update_option('gic_repository_schema_version', 11, false)","add_shortcode('global_impact_catalyst_production_readiness'",'/production-repository','/locales','/offline-packages','/offline-changes','/accessibility-audits','/security-policy','/deployment-environments','/release-readiness']:
    require(marker in php,f'WordPress production contract missing: {marker}')
for table in ['locales','offline_packages','offline_changes','accessibility_audits','security_policies','backup_plans','backup_runs','recovery_tests','deployment_environments','release_readiness']:
    require(f"gic_repository_table('{table}')" in php,f'WordPress table missing: {table}')
for asset in ['global-impact-catalyst-production.js','global-impact-catalyst-production.css']:
    require((ROOT/'wordpress/global-impact-catalyst-demo/assets'/asset).exists(),f'WordPress asset missing: {asset}')

schema_examples={
 'global_impact_production_repository.schema.json':'example_global_impact_production_repository.json',
 'global_impact_workspace_bundle.schema.json':'example_global_impact_workspace_bundle.json'}
for schema_name,example_name in schema_examples.items():
    schema=load('schemas/'+schema_name); example=load('examples/'+example_name)
    require(schema.get('x-global-impact-catalyst-version')==PACKAGE,f'{schema_name} version marker missing')
    for err in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(example): errors.append(f'{example_name}: {err.message}')

migration=read('migrations/011_accessibility_offline_localization_production_hardening.sql')
for table in ['locale_definitions','offline_packages','offline_change_queue','accessibility_audits','security_policies','backup_plans','backup_runs','recovery_tests','deployment_environments','release_readiness_checks']:
    require(re.search(rf'CREATE TABLE IF NOT EXISTS\s+{table}\b',migration,re.I) is not None,f'migration 11 table missing: {table}')
for path in ['README.md','CHANGELOG.md','release/v1.10.0.md','docs/accessibility-offline-localization-production-hardening.md','docs/offline-and-sync.md','docs/localization.md','docs/security-backup-recovery.md']:
    require('1.10.0' in read(path) or path.startswith('docs/'),f'v1.10.0 documentation marker missing: {path}')
require('Accessibility, Offline Use, Localization, and Production Hardening' in read('README.md'),'README release title missing')

if errors:
    print('Global Impact Catalyst v1.10.0 release contract FAILED:',file=sys.stderr)
    for error in errors: print(f'- {error}',file=sys.stderr)
    raise SystemExit(1)
print('Global Impact Catalyst v1.10.0 release contract passed.')
