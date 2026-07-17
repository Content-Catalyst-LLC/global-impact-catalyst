#!/usr/bin/env python3
from __future__ import annotations
import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
SUBPROCESS_ENV=os.environ.copy()
SUBPROCESS_ENV.setdefault('PYTEST_DISABLE_PLUGIN_AUTOLOAD','1')
def run(*args): subprocess.run(args,cwd=ROOT,check=True,env=SUBPROCESS_ENV)
def main():
    if os.environ.get('GIC_SKIP_PYTEST') == '1':
        print('INFO: pytest suite skipped; running deterministic installed-repository gates.')
    else:
        run(sys.executable,'-m','pytest','-q')
    run(sys.executable,'scripts/check_contracts.py')
    if shutil.which('node'):
        run('node','scripts/check_browser_parity.js')
        run('node','--check','wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js')
        run('node','--check','wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-workspace.js')
    else: print('INFO: Node unavailable; browser checks skipped by portable smoke test.')
    if shutil.which('php'):
        run('php','-l','wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
        run('php','scripts/check_wordpress_instances.php')
    else: print('INFO: PHP unavailable; WordPress checks skipped by portable smoke test.')
    with tempfile.TemporaryDirectory(prefix='gic-v120-') as directory:
        directory=Path(directory)
        output=directory/'contract.json'; brief=directory/'brief.md'; database=directory/'impact.sqlite3'
        bundle_path=directory/'workspace-bundle.json'; backup=directory/'impact-backup.sqlite3'
        run(sys.executable,'python/global_impact_core.py','--input','data/sample_global_impact_input.json','--output',str(output),'--markdown',str(brief),'--generated-at','2026-07-17T18:00:00+00:00')
        contract=json.loads(output.read_text())
        assert contract['contract_version']=='1.1.0'
        assert contract['derived']['metrics']['progress_to_target_percent']==60.0
        contract_schema=json.loads((ROOT/'schemas/global_impact_contract.schema.json').read_text())
        assert not list(Draft202012Validator(contract_schema,format_checker=FormatChecker()).iter_errors(contract))
        subprocess.run([sys.executable,'scripts/gic_repository.py','--database',str(database),'init'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,env=SUBPROCESS_ENV)
        subprocess.run([sys.executable,'scripts/gic_repository.py','--database',str(database),'create','--input','data/sample_global_impact_input.json','--generated-at','2026-07-17T18:00:00+00:00'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,env=SUBPROCESS_ENV)
        summary=json.loads(subprocess.check_output([sys.executable,'scripts/gic_repository.py','--database',str(database),'summary'],cwd=ROOT,text=True,env=SUBPROCESS_ENV))
        assert summary['database_schema_version']==3 and summary['contracts']==1 and summary['initiatives']==1
        from python.global_impact_repository import SQLiteImpactRepository
        with SQLiteImpactRepository(database) as repository:
            workspace_id=repository.list_entities('workspace')[0]['entity_id']
            stored=repository.get_contract(initiative_id=repository.list_entities('initiative')[0]['entity_id'])
            assert stored['contract']['derived']['metrics']==contract['derived']['metrics']
        subprocess.run([sys.executable,'scripts/gic_repository.py','--database',str(database),'export','--workspace-id',workspace_id,'--output',str(bundle_path)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,env=SUBPROCESS_ENV)
        bundle=json.loads(bundle_path.read_text())
        bundle_schema=json.loads((ROOT/'schemas/global_impact_workspace_bundle.schema.json').read_text())
        assert not list(Draft202012Validator(bundle_schema,format_checker=FormatChecker()).iter_errors(bundle))
        subprocess.run([sys.executable,'scripts/gic_repository.py','--database',str(database),'backup','--output',str(backup)],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,env=SUBPROCESS_ENV)
        assert backup.exists() and backup.stat().st_size>0
        from python.global_impact_service import ImpactApplicationService
        legacy=json.loads((ROOT/'contracts/legacy/legacy-v1.0.1-record.json').read_text())
        with SQLiteImpactRepository(database) as repository:
            service=ImpactApplicationService(repository)
            imported=service.import_document(legacy,generated_at='2026-07-17T18:00:00+00:00')
            repeated=service.import_document(legacy,generated_at='2026-07-17T18:00:00+00:00')
            assert imported.status=='imported' and repeated.status=='unchanged'
            assert repository.repository_summary()['imports']==1
    print('Global Impact Catalyst v1.2.0 portable release smoke tests passed.')
    return 0
if __name__=='__main__': raise SystemExit(main())
