from __future__ import annotations
import json,sqlite3
from pathlib import Path

import pytest

from python.global_impact_core import build_impact_contract,input_from_dict
from python.global_impact_repository import (
    DATABASE_SCHEMA_VERSION,NotFoundError,OptimisticConcurrencyError,SQLiteImpactRepository,
)
from python.global_impact_service import ImpactApplicationService,compact_input_from_contract

ROOT=Path(__file__).resolve().parents[1]
FIXED='2026-07-17T18:00:00+00:00'

def sample_payload(): return json.loads((ROOT/'data/sample_global_impact_input.json').read_text())
def sample_contract(): return build_impact_contract(input_from_dict(sample_payload()),generated_at=FIXED)

@pytest.mark.parametrize('target',[1,2,3])
def test_migrations_are_repeatable_from_every_supported_database_version(tmp_path,target):
    path=tmp_path/f'migration-{target}.sqlite3'
    repo=SQLiteImpactRepository(path,auto_migrate=False)
    assert repo.schema_version==0
    assert repo.migrate(target)==target
    assert repo.migrate(target)==target
    assert [item['version'] for item in repo.applied_migrations()]==list(range(1,target+1))
    if target<DATABASE_SCHEMA_VERSION:
        assert repo.migrate()==DATABASE_SCHEMA_VERSION
    repo.close()


def test_create_close_and_reopen_complete_workspace(tmp_path):
    database=tmp_path/'impact.sqlite3'
    repo=SQLiteImpactRepository(database)
    service=ImpactApplicationService(repo)
    created=service.create_initiative(sample_payload(),generated_at=FIXED)
    meta=created['repository']; expected=created['contract']
    assert repo.repository_summary()['contracts']==1
    repo.close()

    reopened=SQLiteImpactRepository(database)
    stored=reopened.get_contract(record_id=meta['record_id'])
    assert stored['contract']==expected
    assert stored['contract']['facts']['measurement']['observations'][0]['value']==18.0
    assert stored['contract']['derived']['metrics']==expected['derived']['metrics']
    for entity_type in ('workspace','initiative','goal','indicator','observation','target','source'):
        assert reopened.list_entities(entity_type,workspace_id=meta['workspace_id'])
    reopened.close()


def test_entity_crud_and_optimistic_concurrency(tmp_path):
    repo=SQLiteImpactRepository(tmp_path/'crud.sqlite3')
    service=ImpactApplicationService(repo)
    created=service.create_initiative(sample_payload(),generated_at=FIXED)
    source_id=created['contract']['facts']['sources'][0]['id']
    source=repo.get_entity('source',source_id)
    updated=repo.update_entity('source',source_id,{'title':'Updated evidence package'},expected_revision=source['revision'])
    assert updated['document']['title']=='Updated evidence package'
    with pytest.raises(OptimisticConcurrencyError) as error:
        repo.update_entity('source',source_id,{'title':'Stale edit'},expected_revision=source['revision'])
    assert error.value.actual_revision==updated['revision']
    repo.delete_entity('source',source_id,expected_revision=updated['revision'])
    with pytest.raises(NotFoundError): repo.get_entity('source',source_id,include_archived=True)
    repo.close()


def test_save_autosave_and_conflict_responses(tmp_path):
    repo=SQLiteImpactRepository(tmp_path/'save.sqlite3')
    service=ImpactApplicationService(repo)
    created=service.create_initiative(sample_payload(),generated_at=FIXED)
    contract=created['contract']; meta=created['repository']
    draft=json.loads(json.dumps(contract)); draft['facts']['goal']['statement']='Autosaved goal edit'
    autosave=service.autosave_initiative(draft,base_revision=meta['revision'],actor='editor')
    assert autosave['base_revision']==1
    assert repo.get_autosave(meta['initiative_id'])['contract']['facts']['goal']['statement']=='Autosaved goal edit'
    saved=service.save_initiative(draft,expected_revision=1,generated_at='2026-07-18T12:00:00+00:00',actor='editor',allow_invalid=True)
    assert saved['repository']['revision']==2
    assert repo.get_autosave(meta['initiative_id']) is None
    with pytest.raises(OptimisticConcurrencyError):
        service.save_initiative(draft,expected_revision=1,generated_at='2026-07-18T13:00:00+00:00',allow_invalid=True)
    repo.close()


def test_lists_search_archive_restore_and_duplicate(tmp_path):
    repo=SQLiteImpactRepository(tmp_path/'lists.sqlite3')
    service=ImpactApplicationService(repo)
    first=service.create_initiative(sample_payload(),generated_at=FIXED)
    duplicated=service.duplicate_initiative(first['repository']['initiative_id'],new_name='Neighborhood Heat Pump Portfolio',generated_at='2026-07-18T00:00:00+00:00')
    workspace_id=first['repository']['workspace_id']
    assert len(service.list_initiatives(workspace_id=workspace_id))==2
    matches=service.list_initiatives(workspace_id=workspace_id,search='heat pump')
    assert [item['name'] for item in matches]==['Neighborhood Heat Pump Portfolio']
    duplicate_id=duplicated['repository']['initiative_id']
    entity=repo.get_entity('initiative',duplicate_id)
    archived=repo.archive_entity('initiative',duplicate_id,expected_revision=entity['revision'])
    assert archived['archived_at']
    assert len(service.list_initiatives(workspace_id=workspace_id))==1
    assert len(service.list_initiatives(workspace_id=workspace_id,include_archived=True))==2
    restored=repo.restore_entity('initiative',duplicate_id,expected_revision=archived['revision'])
    assert restored['archived_at'] is None
    assert duplicated['contract']['record_id']!=first['contract']['record_id']
    assert duplicated['contract']['derived']['metrics']==first['contract']['derived']['metrics']
    repo.close()


def test_portfolios_manage_multiple_initiatives(tmp_path):
    repo=SQLiteImpactRepository(tmp_path/'portfolios.sqlite3')
    service=ImpactApplicationService(repo)
    first=service.create_initiative(sample_payload(),generated_at=FIXED)
    second=service.duplicate_initiative(first['repository']['initiative_id'],new_name='Second Initiative',generated_at='2026-07-18T00:00:00+00:00')
    workspace_id=first['repository']['workspace_id']
    portfolio=repo.create_portfolio('portfolio-community',workspace_id,'Community programs','Cross-initiative view')
    repo.add_to_portfolio(portfolio['portfolio_id'],first['repository']['initiative_id'])
    result=repo.add_to_portfolio(portfolio['portfolio_id'],second['repository']['initiative_id'],position=2)
    assert set(result['initiative_ids'])=={first['repository']['initiative_id'],second['repository']['initiative_id']}
    result=repo.remove_from_portfolio(portfolio['portfolio_id'],second['repository']['initiative_id'])
    assert result['initiative_ids']==[first['repository']['initiative_id']]
    assert repo.list_portfolios(workspace_id,search='community')[0]['name']=='Community programs'
    repo.close()


def test_v101_and_v110_imports_are_idempotent_and_audited(tmp_path):
    repo=SQLiteImpactRepository(tmp_path/'imports.sqlite3')
    service=ImpactApplicationService(repo)
    legacy=json.loads((ROOT/'contracts/legacy/legacy-v1.0.1-record.json').read_text())
    first=service.import_document(legacy,generated_at=FIXED)
    second=service.import_document(legacy,generated_at=FIXED)
    assert first.status=='imported'
    assert second.status=='unchanged'
    assert first.import_id==second.import_id
    canonical=sample_contract()
    third=service.import_document(canonical)
    fourth=service.import_document(canonical)
    assert third.status=='imported'
    assert fourth.status=='unchanged'
    audit=repo.audit_records(limit=100)
    assert any(item['action']=='import' and item['details'].get('import_id')==first.import_id for item in audit)
    assert repo.repository_summary()['imports']==2
    repo.close()


def test_workspace_export_restore_bundle_is_repeatable(tmp_path):
    source=SQLiteImpactRepository(tmp_path/'source.sqlite3')
    service=ImpactApplicationService(source)
    first=service.create_initiative(sample_payload(),generated_at=FIXED)
    second=service.duplicate_initiative(first['repository']['initiative_id'],new_name='Second Initiative',generated_at='2026-07-18T00:00:00+00:00')
    portfolio=source.create_portfolio('portfolio-all',first['repository']['workspace_id'],'All initiatives')
    source.add_to_portfolio(portfolio['portfolio_id'],first['repository']['initiative_id'])
    source.add_to_portfolio(portfolio['portfolio_id'],second['repository']['initiative_id'])
    bundle=service.export_workspace(first['repository']['workspace_id'])
    assert bundle['bundle_type']=='global_impact_workspace_bundle'
    assert len(bundle['contracts'])==2

    target=SQLiteImpactRepository(tmp_path/'target.sqlite3')
    target_service=ImpactApplicationService(target)
    restored=target_service.restore_workspace(bundle)
    repeated=target_service.restore_workspace(bundle)
    assert restored['status']=='restored' and restored['contracts_imported']==2
    assert repeated['status']=='unchanged'
    assert target.repository_summary()['contracts']==2
    assert target.get_portfolio('portfolio-all')['initiative_ids']
    source.close(); target.close()


def test_backup_database_is_openable(tmp_path):
    database=tmp_path/'source.sqlite3'; backup=tmp_path/'backups'/'copy.sqlite3'
    repo=SQLiteImpactRepository(database)
    ImpactApplicationService(repo).create_initiative(sample_payload(),generated_at=FIXED)
    path=repo.backup_database(backup)
    repo.close()
    copied=SQLiteImpactRepository(path)
    assert copied.repository_summary()['contracts']==1
    copied.close()


def test_compact_projection_rebuilds_same_calculations():
    original=sample_contract()
    rebuilt=build_impact_contract(input_from_dict(compact_input_from_contract(original)),generated_at=FIXED)
    assert rebuilt['derived']['metrics']==original['derived']['metrics']
    assert rebuilt['validation']==original['validation']
