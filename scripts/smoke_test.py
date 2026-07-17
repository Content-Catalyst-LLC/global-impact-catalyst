#!/usr/bin/env python3
from __future__ import annotations
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def run(*args): subprocess.run(args,cwd=ROOT,check=True)
def main():
    run(sys.executable,'-m','pytest','-q')
    run(sys.executable,'scripts/check_contracts.py')
    if shutil.which('node'):
        run('node','scripts/check_browser_parity.js')
        run('node','--check','wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-demo.js')
    else: print('INFO: Node unavailable; browser parity skipped by portable smoke test.')
    if shutil.which('php'):
        run('php','-l','wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php')
        run('php','scripts/check_wordpress_instances.php')
    else: print('INFO: PHP unavailable; WordPress checks skipped by portable smoke test.')
    with tempfile.TemporaryDirectory(prefix='gic-v110-') as directory:
        directory=Path(directory)
        output=directory/'contract.json'; brief=directory/'brief.md'; migrated=directory/'migrated.json'
        run(sys.executable,'python/global_impact_core.py','--input','data/sample_global_impact_input.json','--output',str(output),'--markdown',str(brief),'--generated-at','2026-07-17T18:00:00+00:00')
        data=json.loads(output.read_text())
        assert data['contract_type']=='global_impact_contract'
        assert data['contract_version']=='1.1.0'
        assert data['validation']['valid'] is True
        assert data['derived']['metrics']['progress_to_target_percent']==60.0
        assert data['facts']['measurement']['observations'][0]['value']==18.0
        assert brief.read_text().startswith('# Global Impact Contract:')
        schema=json.loads((ROOT/'schemas/global_impact_contract.schema.json').read_text())
        errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(data))
        assert not errors,[e.message for e in errors]
        run(sys.executable,'python/global_impact_core.py','--input','contracts/legacy/legacy-v1.0.1-record.json','--output',str(migrated),'--migrate','--allow-invalid')
        migration=json.loads(migrated.read_text())
        legacy=json.loads((ROOT/'contracts/legacy/legacy-v1.0.1-record.json').read_text())
        assert migration['provenance']['migration']['legacy_record']==legacy
        assert migration['facts']['initiative']['name']==legacy['initiative']
    print('Global Impact Catalyst v1.1.0 portable release smoke tests passed.')
    return 0
if __name__=='__main__': raise SystemExit(main())
