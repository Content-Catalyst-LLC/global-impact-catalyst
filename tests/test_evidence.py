from __future__ import annotations
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_repository import OptimisticConcurrencyError, RepositoryError, SQLiteImpactRepository, checksum_payload
from python.global_impact_service import ImpactApplicationService

ROOT=Path(__file__).resolve().parents[1]
FIXED='2026-07-17T18:00:00+00:00'

def payload(): return json.loads((ROOT/'data/sample_global_impact_input.json').read_text())

def create(repo): return ImpactApplicationService(repo).create_initiative(payload(),generated_at=FIXED)

def test_contract_save_materializes_versioned_sources_and_provenance(tmp_path):
    with SQLiteImpactRepository(tmp_path/'evidence.sqlite3') as repo:
        created=create(repo); chain=repo.evidence_chain(created['repository']['initiative_id'])
        assert chain['integrity']['valid'] is True
        assert chain['integrity']['source_count']==1
        assert chain['integrity']['version_count']==1
        assert chain['integrity']['edge_count']>=9
        assert chain['sources'][0]['versions'][0]['checksum_algorithm']=='sha256'
        assert len(chain['sources'][0]['versions'][0]['checksum_value'])==64

def test_source_registry_supports_revision_control_and_search(tmp_path):
    with SQLiteImpactRepository(tmp_path/'sources.sqlite3') as repo:
        created=create(repo); meta=created['repository']
        source=repo.register_source({'title':'Independent evaluation','doi':'10.1234/example','license':'CC-BY-4.0'},workspace_id=meta['workspace_id'],initiative_id=meta['initiative_id'])
        updated=repo.register_source({**source,'title':'Independent evaluation report','metadata':source['metadata']},workspace_id=meta['workspace_id'],initiative_id=meta['initiative_id'],expected_revision=1)
        assert updated['revision']==2
        assert repo.list_sources(search='evaluation report')[0]['source_id']==source['source_id']
        with pytest.raises(OptimisticConcurrencyError):
            repo.register_source({'source_id':source['source_id'],'title':'Stale edit'},workspace_id=meta['workspace_id'],initiative_id=meta['initiative_id'],expected_revision=1)

def test_source_versions_are_checksum_verified_and_idempotent(tmp_path):
    with SQLiteImpactRepository(tmp_path/'versions.sqlite3') as repo:
        created=create(repo); source_id=repo.evidence_chain(created['repository']['initiative_id'])['sources'][0]['source_id']
        text='verified source payload'
        version=repo.add_source_version(source_id,version_label='published PDF',payload=text,mime_type='text/plain',captured_by='reviewer')
        repeated=repo.add_source_version(source_id,version_label='published PDF',payload=text,mime_type='text/plain',captured_by='reviewer')
        assert version['source_version_id']==repeated['source_version_id']
        assert version['checksum_value']==checksum_payload(text)
        with pytest.raises(RepositoryError):
            repo.add_source_version(source_id,payload=text,checksum_value='0'*64)

def test_evidence_capture_dataset_and_claim_link_build_complete_chain(tmp_path):
    with SQLiteImpactRepository(tmp_path/'chain.sqlite3') as repo:
        created=create(repo); initiative_id=created['repository']['initiative_id']
        source=repo.evidence_chain(initiative_id)['sources'][0]
        evidence=repo.capture_evidence(source['source_id'],evidence_type='quotation',title='Observed bill reduction',locator='p. 14',exact_quote='Average monthly bills declined by eighteen dollars.',captured_by='analyst')
        dataset=repo.register_dataset(source['source_id'],{'title':'Participant billing panel','version':'2026-Q2','license':'restricted-internal','checksum_value':'a'*64,'schema_fingerprint':'b'*64,'row_count':420,'column_count':18})
        claim_id=created['contract']['derived']['claims'][0]['id']
        link=repo.link_claim_evidence(claim_id,evidence['evidence_id'],relationship='supports',strength='direct',linked_by='reviewer')
        chain=repo.evidence_chain(initiative_id)
        assert dataset['dataset_id']==chain['datasets'][0]['dataset_id']
        assert link['evidence_id']==chain['claim_evidence_links'][0]['evidence_id']
        assert chain['integrity']['evidence_count']==1
        assert chain['integrity']['dataset_count']==1
        assert chain['integrity']['claim_link_count']==1
        assert chain['integrity']['valid'] is True

def test_contradicting_evidence_is_reported_not_silently_removed(tmp_path):
    with SQLiteImpactRepository(tmp_path/'contradiction.sqlite3') as repo:
        created=create(repo); initiative_id=created['repository']['initiative_id']
        source=repo.evidence_chain(initiative_id)['sources'][0]
        evidence=repo.capture_evidence(source['source_id'],notes='A subgroup result moves in the opposite direction.')
        claim_id=created['contract']['derived']['claims'][0]['id']
        repo.link_claim_evidence(claim_id,evidence['evidence_id'],relationship='contradicts',strength='indirect')
        chain=repo.evidence_chain(initiative_id)
        assert chain['integrity']['contradicting_link_count']==1
        assert chain['claim_evidence_links'][0]['relationship']=='contradicts'

def test_workspace_export_restore_preserves_full_evidence_repository(tmp_path):
    with SQLiteImpactRepository(tmp_path/'source.sqlite3') as source_repo:
        created=create(source_repo); initiative_id=created['repository']['initiative_id']; workspace_id=created['repository']['workspace_id']
        source=source_repo.evidence_chain(initiative_id)['sources'][0]
        evidence=source_repo.capture_evidence(source['source_id'],exact_quote='Traceable excerpt',locator='table 2')
        source_repo.link_claim_evidence(created['contract']['derived']['claims'][0]['id'],evidence['evidence_id'])
        source_repo.register_dataset(source['source_id'],{'title':'Traceable dataset','checksum_value':'c'*64})
        bundle=source_repo.export_workspace_bundle(workspace_id)
        assert bundle['bundle_version']=='1.7.0'
        assert bundle['evidence_repository']['source_versions']
    with SQLiteImpactRepository(tmp_path/'target.sqlite3') as target_repo:
        result=target_repo.restore_workspace_bundle(bundle)
        chain=target_repo.evidence_chain(initiative_id)
        assert result['status']=='restored'
        assert chain['integrity']['evidence_count']==1
        assert chain['integrity']['dataset_count']==1
        assert chain['integrity']['claim_link_count']==1

def test_evidence_chain_and_repository_exports_validate_against_schemas(tmp_path):
    with SQLiteImpactRepository(tmp_path/'schema.sqlite3') as repo:
        created=create(repo); initiative_id=created['repository']['initiative_id']; workspace_id=created['repository']['workspace_id']
        chain=repo.evidence_chain(initiative_id)
        evidence_repository=repo.export_evidence_repository(workspace_id)
    chain_schema=json.loads((ROOT/'schemas/global_impact_evidence_chain.schema.json').read_text())
    repository_schema=json.loads((ROOT/'schemas/global_impact_evidence_repository.schema.json').read_text())
    assert not list(Draft202012Validator(chain_schema,format_checker=FormatChecker()).iter_errors(chain))
    assert not list(Draft202012Validator(repository_schema,format_checker=FormatChecker()).iter_errors(evidence_repository))
