#!/usr/bin/env python3
"""Repository and release invariants for Global Impact Catalyst v1.7.0."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]
PACKAGE='1.7.0'; CONTRACT='1.1.0'; EVIDENCE='1.3.0'; REGISTRY='1.4.0'; MEASUREMENT='1.5.0'; REVIEW='1.6.0'; DATABASE=8
errors=[]
def require(ok,msg):
    if not ok: errors.append(msg)
def read(path): return (ROOT/path).read_text(encoding='utf-8')
def load(path): return json.loads(read(path))
manifest=load('global_impact_catalyst_manifest.json')
for k,v in [('version',PACKAGE),('contract_version',CONTRACT),('database_schema_version',DATABASE),('workspace_bundle_version',PACKAGE),('evidence_chain_version',EVIDENCE),('indicator_registry_version',REGISTRY),('measurement_repository_version',MEASUREMENT),('review_workflow_version',REVIEW),('analysis_repository_version',PACKAGE),('analysis_shortcode','[global_impact_catalyst_analysis_studio]')]: require(manifest.get(k)==v,f'manifest {k} mismatch')
for k in ['core_path','repository_path','service_path','repository_cli_path','workspace_bundle_schema_path','analysis_module_path','analysis_repository_schema_path','analysis_doc_path','comparison_governance_doc_path','scenario_uncertainty_doc_path','analysis_repository_example_path','database_migration_8']:
    v=manifest.get(k); require(v and (ROOT/v).exists(),f'manifest path missing: {k} -> {v}')
required={'trend_analysis','benchmark_registry','benchmark_comparisons','comparison_sets','guarded_rankings','scenario_registry','linear_scenarios','compound_scenarios','step_scenarios','uncertainty_models','sensitivity_analysis','analysis_run_history','analysis_repository_export'}
require(required.issubset(set(manifest.get('repository_capabilities',[]))),'analysis capabilities incomplete')
repo=read('python/global_impact_repository.py')
for n in ['DATABASE_SCHEMA_VERSION = 8','AnalysisScenarioMixin','008_trends_comparisons_scenarios_uncertainty.sql','"bundle_version": "1.7.0"','"analysis_repository": self.export_analysis_repository(workspace_id)','self._restore_analysis_repository','"analysis_runs": count("analysis_runs")']: require(n in repo,f'repository contract missing: {n}')
analysis=read('python/global_impact_analysis.py')
for n in ['ANALYSIS_VERSION = "1.7.0"','def analyze_trend','def register_benchmark','def compare_to_benchmark','def create_comparison_set','def run_comparison_set','def register_uncertainty_model','def register_scenario','def evaluate_scenario','def run_sensitivity_analysis','def compare_observations_to_target','def export_analysis_repository','def _restore_analysis_repository']: require(n in analysis,f'analysis contract missing: {n}')
service=read('python/global_impact_service.py')
for n in ['SERVICE_VERSION = "1.7.0"','def analyze_trend','def register_benchmark','def register_scenario','def run_sensitivity_analysis','def analysis_repository']: require(n in service,f'service contract missing: {n}')
app=read('app/main.py')
for n in ['"version": "1.7.0"','"database_schema_version": 8','"review_workflow_version": "1.6.0"','"analysis_repository_version": "1.7.0"']: require(n in app,f'application contract missing: {n}')
cli=read('scripts/gic_repository.py')
for cmd in ['trend','add-benchmark','compare-benchmark','add-comparison-set','run-comparison-set','add-uncertainty','apply-uncertainty','add-scenario','evaluate-scenario','sensitivity','target-trajectory','analysis-repository']: require(f"'{cmd}'" in cli,f'CLI command missing: {cmd}')
assets=ROOT/'wordpress/global-impact-catalyst-demo/assets'
for a in ['global-impact-catalyst-demo.js','global-impact-catalyst-workspace.js','global-impact-catalyst-evidence.js','global-impact-catalyst-registry.js','global-impact-catalyst-measurement.js','global-impact-catalyst-review.js','global-impact-catalyst-analysis.js','global-impact-catalyst-analysis.css']: require((assets/a).exists() and (assets/a).stat().st_size>100,f'WordPress asset missing: {a}')
plugin=read('wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
header=re.search(r'^ \* Version:\s*([^\s]+)',plugin,re.M); const=re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)",plugin)
require(header and header.group(1)==PACKAGE,'WordPress header mismatch'); require(const and const.group(1)==PACKAGE,'WordPress constant mismatch')
for n in ["add_shortcode('global_impact_catalyst_analysis_studio'",'/analysis-repository','/analysis-benchmarks','/analysis-uncertainty-models','/analysis-scenarios','/analysis-trends','/analysis-comparison-sets',"gic_repository_table('analysis_benchmarks')","gic_repository_table('analysis_runs')"]: require(n in plugin,f'WordPress analysis contract missing: {n}')
versions={'global_impact_input.schema.json':CONTRACT,'global_impact_contract.schema.json':CONTRACT,'global_impact_record.schema.json':CONTRACT,'global_impact_validation_result.schema.json':CONTRACT,'global_impact_evidence_chain.schema.json':EVIDENCE,'global_impact_evidence_repository.schema.json':EVIDENCE,'global_impact_indicator_registry.schema.json':REGISTRY,'global_impact_measurement_repository.schema.json':MEASUREMENT,'global_impact_review_workflow.schema.json':REVIEW,'global_impact_analysis_repository.schema.json':PACKAGE,'global_impact_workspace_bundle.schema.json':PACKAGE}
for name,version in versions.items():
    schema=load('schemas/'+name); require(schema.get('x-global-impact-catalyst-version')==version,f'schema version mismatch: {name}'); require(f'/{version}/' in schema.get('$id',''),f'schema id mismatch: {name}')
for example,schema in [('examples/example_global_impact_analysis_repository.json','global_impact_analysis_repository.schema.json'),('examples/example_global_impact_workspace_bundle.json','global_impact_workspace_bundle.schema.json'),('examples/example_global_impact_review_workflow.json','global_impact_review_workflow.schema.json')]:
    es=list(Draft202012Validator(load('schemas/'+schema),format_checker=FormatChecker()).iter_errors(load(example))); require(not es,f'example schema failure: {example}: {[e.message for e in es]}')
migrations=[p.name for p in sorted((ROOT/'migrations').glob('*.sql'))]
require(migrations==['001_core_repository.sql','002_portfolios_and_autosave.sql','003_imports_audit_and_bundles.sql','004_sources_provenance_evidence.sql','005_indicator_registry_units_baselines_targets_methods.sql','006_observations_beneficiaries_budgets_outcome_portfolios.sql','007_review_quality_revision_workflow.sql','008_trends_comparisons_scenarios_uncertainty.sql'],'database migration inventory mismatch')
for path in ['docs/trends-comparisons-scenarios-uncertainty.md','docs/comparison-governance.md','docs/scenario-and-uncertainty-governance.md','release/v1.7.0.md']:
    require((ROOT/path).exists() and (ROOT/path).stat().st_size>300,f'documentation missing: {path}')
require('1.7.0' in read('CHANGELOG.md') and 'Trends, Comparisons, Scenarios, and Uncertainty' in read('CHANGELOG.md'),'CHANGELOG missing v1.7.0')
require('global_impact_catalyst_analysis_studio' in read('README.md'),'README missing analysis shortcode')
if errors:
    print('\n'.join('ERROR: '+e for e in errors)); raise SystemExit(1)
print('Global Impact Catalyst v1.7.0 release contract passed.')
