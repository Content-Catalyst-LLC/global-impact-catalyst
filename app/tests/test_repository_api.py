import json
from pathlib import Path
from app.main import healthcheck,open_application

ROOT=Path(__file__).resolve().parents[2]

def test_application_health_reports_persistence_contract():
    health=healthcheck()
    assert health['version']=='1.3.0'
    assert health['contract_version']=='1.1.0'
    assert health['database_schema_version']==4
    assert health['persistence']=='sqlite'


def test_open_application_uses_shared_service(tmp_path):
    service=open_application(tmp_path/'app.sqlite3')
    payload=json.loads((ROOT/'data/sample_global_impact_input.json').read_text())
    created=service.create_initiative(payload,generated_at='2026-07-17T18:00:00+00:00')
    assert created['repository']['revision']==1
    assert service.repository.repository_summary()['initiatives']==1
    service.repository.close()
