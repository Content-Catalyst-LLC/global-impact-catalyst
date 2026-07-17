#!/usr/bin/env python3
from __future__ import annotations
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
SUBPROCESS_ENV=os.environ.copy(); SUBPROCESS_ENV.setdefault('PYTEST_DISABLE_PLUGIN_AUTOLOAD','1')
def run(*args,stdout=None): subprocess.run(args,cwd=ROOT,check=True,env=SUBPROCESS_ENV,stdout=stdout)
def validate(document,schema_name):
    schema=json.loads((ROOT/'schemas'/schema_name).read_text())
    errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(document))
    assert not errors, '\n'.join(error.message for error in errors[:10])
def main():
    if os.environ.get('GIC_SKIP_PYTEST')=='1': print('INFO: pytest suite skipped; running deterministic installed-repository gates.')
    else: run(sys.executable,'-m','pytest','-q')
    run(sys.executable,'scripts/check_contracts.py')
    if shutil.which('node'):
        run('node','scripts/check_browser_parity.js')
        for asset in ('global-impact-catalyst-demo.js','global-impact-catalyst-workspace.js','global-impact-catalyst-evidence.js'):
            run('node','--check',f'wordpress/global-impact-catalyst-demo/assets/{asset}')
    else: print('INFO: Node unavailable; browser checks skipped by portable smoke test.')
    if shutil.which('php'):
        run('php','-l','wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
        run('php','scripts/check_wordpress_instances.php')
    else: print('INFO: PHP unavailable; WordPress checks skipped by portable smoke test.')
    with tempfile.TemporaryDirectory(prefix='gic-v130-') as temp:
        d=Path(temp); contract_path=d/'contract.json'; brief=d/'brief.md'; database=d/'impact.sqlite3'; restored_db=d/'restored.sqlite3'; bundle_path=d/'workspace-bundle.json'; chain_path=d/'evidence-chain.json'; backup=d/'impact-backup.sqlite3'
        run(sys.executable,'python/global_impact_core.py','--input','data/sample_global_impact_input.json','--output',str(contract_path),'--markdown',str(brief),'--generated-at','2026-07-17T18:00:00+00:00')
        contract=json.loads(contract_path.read_text()); assert contract['contract_version']=='1.1.0'; assert contract['derived']['metrics']['progress_to_target_percent']==60.0
        validate(contract,'global_impact_contract.schema.json')
        run(sys.executable,'scripts/gic_repository.py','--database',str(database),'init',stdout=subprocess.DEVNULL)
        run(sys.executable,'scripts/gic_repository.py','--database',str(database),'create','--input','data/sample_global_impact_input.json','--generated-at','2026-07-17T18:00:00+00:00',stdout=subprocess.DEVNULL)
        from python.global_impact_repository import SQLiteImpactRepository
        from python.global_impact_service import ImpactApplicationService
        with SQLiteImpactRepository(database) as repo:
            summary=repo.repository_summary(); assert summary['database_schema_version']==4 and summary['contracts']==1 and summary['sources']==1 and summary['source_versions']==1 and summary['provenance_edges']>=9
            workspace_id=repo.list_entities('workspace')[0]['entity_id']; initiative_id=repo.list_entities('initiative')[0]['entity_id']
            stored=repo.get_contract(initiative_id=initiative_id); source=repo.evidence_chain(initiative_id)['sources'][0]
            evidence=repo.capture_evidence(source['source_id'],evidence_type='quotation',title='Portable release evidence',locator='p. 14',exact_quote='Average monthly bills declined by eighteen dollars.',captured_by='release-smoke')
            repo.register_dataset(source['source_id'],{'title':'Portable release dataset','version':'1','license':'restricted-internal','checksum_value':'a'*64,'schema_fingerprint':'b'*64,'row_count':420,'column_count':18},actor='release-smoke')
            claim_id=stored['contract']['derived']['claims'][0]['id']; repo.link_claim_evidence(claim_id,evidence['evidence_id'],relationship='supports',strength='direct',linked_by='release-smoke')
            chain=repo.evidence_chain(initiative_id); chain_path.write_text(json.dumps(chain,indent=2))
            assert chain['integrity']['valid'] and chain['integrity']['version_count']==1 and chain['integrity']['evidence_count']==1 and chain['integrity']['dataset_count']==1 and chain['integrity']['claim_link_count']==1
            validate(chain,'global_impact_evidence_chain.schema.json')
            evidence_export=repo.export_evidence_repository(workspace_id); validate(evidence_export,'global_impact_evidence_repository.schema.json')
            bundle=repo.export_workspace_bundle(workspace_id); bundle_path.write_text(json.dumps(bundle,indent=2)); validate(bundle,'global_impact_workspace_bundle.schema.json')
            repo.backup_database(backup)
        assert backup.exists() and backup.stat().st_size>0
        with SQLiteImpactRepository(restored_db) as repo:
            result=repo.restore_workspace_bundle(json.loads(bundle_path.read_text())); assert result['status']=='restored'
            restored=repo.evidence_chain(initiative_id); assert restored['integrity']['valid'] and restored['integrity']['evidence_count']==1 and restored['integrity']['dataset_count']==1 and restored['integrity']['claim_link_count']==1
            repeated=repo.restore_workspace_bundle(json.loads(bundle_path.read_text())); assert repeated['status']=='unchanged'
        legacy=json.loads((ROOT/'contracts/legacy/legacy-v1.0.1-record.json').read_text())
        with SQLiteImpactRepository(database) as repo:
            service=ImpactApplicationService(repo); imported=service.import_document(legacy,generated_at='2026-07-17T18:00:00+00:00'); repeated=service.import_document(legacy,generated_at='2026-07-17T18:00:00+00:00')
            assert imported.status=='imported' and repeated.status=='unchanged'
    print('Global Impact Catalyst v1.3.0 portable release smoke tests passed.')
    return 0
if __name__=='__main__': raise SystemExit(main())
