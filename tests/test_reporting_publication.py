from __future__ import annotations
import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_reporting import ReportingError
from python.global_impact_service import ImpactApplicationService

ROOT=Path(__file__).resolve().parents[1]
FIXED="2026-07-17T20:00:00+00:00"

def payload(): return json.loads((ROOT/'data/sample_global_impact_input.json').read_text())

def create(repo):
    result=ImpactApplicationService(repo).create_initiative(payload(),generated_at=FIXED,actor='owner')
    m=result['repository']; return result,m['workspace_id'],m['initiative_id'],m['record_id']

def approve_and_publish(repo, workspace_id, initiative_id, record_id):
    role=next(x for x in repo.list_workflow_roles(workspace_id) if x['metadata'].get('role_key')=='approver')
    assignment=repo.create_review_assignment({'subject_type':'contract','subject_id':record_id,'reviewer_id':'approver@example.org','role_id':role['role_id']},workspace_id=workspace_id,initiative_id=initiative_id)
    repo.submit_quality_assessment({'assessor_id':'approver@example.org','dimensions':[{'key':'evidence','score':90,'maximum_score':100},{'key':'method','score':85,'maximum_score':100}]},workspace_id=workspace_id,initiative_id=initiative_id,assignment_id=assignment['assignment_id'])
    repo.record_approval_decision(assignment['assignment_id'],'approve',rationale='Approved.',reviewer_id='approver@example.org')
    publication=repo.create_publication({'subject_type':'contract','subject_id':record_id,'title':'Public Impact Report','release_label':'2026 Q2'},workspace_id=workspace_id,initiative_id=initiative_id)
    return repo.publish(publication['publication_id'],actor='publisher')

def test_migration_9_and_template_concurrency(tmp_path):
    with SQLiteImpactRepository(tmp_path/'reporting.sqlite3') as repo:
        _,w,_,_=create(repo)
        assert DATABASE_SCHEMA_VERSION==9 and repo.schema_version==9
        template=repo.register_report_template({'name':'Public impact report','sections':['executive_summary','results','methodology','references'],'citation_style':'harvard'},workspace_id=w)
        assert template['revision']==1 and template['accessibility_profile']['wcag_target']=='2.2 AA'
        updated=repo.register_report_template({**template,'description':'Reviewed public template'},workspace_id=w,expected_revision=1)
        assert updated['revision']==2
        with pytest.raises(Exception): repo.register_report_template({**template,'description':'stale'},workspace_id=w,expected_revision=1)

def test_accessible_report_citations_and_methodology(tmp_path):
    with SQLiteImpactRepository(tmp_path/'report.sqlite3') as repo:
        _,w,i,_=create(repo)
        template=repo.register_report_template({'name':'Accessible report','citation_style':'harvard'},workspace_id=w)
        report=repo.create_report({'title':'Community Energy Impact Report','period_label':'2026 Q2'},workspace_id=w,initiative_id=i,template_id=template['template_id'],actor='editor')
        assert report['content_hash'] and report['document']['initiative']['id']==i
        assert '<html lang="en">' in report['rendered_html'] and 'Skip to report' in report['rendered_html']
        assert '## Methodology appendix' in report['rendered_markdown']
        assert report['citations'] and report['citations'][0]['source_id']
        assert report['methodology']['canonical_contract_version']=='1.1.0'
        assert repo.export_reporting_repository(w)['integrity']['valid']

def test_dashboard_cards_and_accessibility(tmp_path):
    with SQLiteImpactRepository(tmp_path/'dashboard.sqlite3') as repo:
        _,w,i,_=create(repo)
        dash=repo.create_dashboard({'name':'Impact overview','audience':'board','layout':{'columns':2}},workspace_id=w,initiative_id=i)
        repo.add_dashboard_card(dash['dashboard_id'],{'card_type':'metric','title':'Observed reduction','alt_text':'Observed monthly bill reduction in US dollars','configuration':{'value':18,'unit':'USD'},'position':1})
        repo.add_dashboard_card(dash['dashboard_id'],{'card_type':'quality','title':'Review quality','alt_text':'Review workflow integrity summary','position':2})
        rendered=repo.render_dashboard(dash['dashboard_id'])
        assert rendered['accessibility']=={'card_count':2,'all_cards_have_alt_text':True}
        assert rendered['cards'][0]['value']==18

def test_publication_snapshot_and_reproducible_export(tmp_path):
    path1=tmp_path/'export-one.zip'; path2=tmp_path/'export-two.zip'
    with SQLiteImpactRepository(tmp_path/'export.sqlite3') as repo:
        _,w,i,r=create(repo)
        report=repo.create_report({'title':'Release Report','period_label':'2026 Q2'},workspace_id=w,initiative_id=i)
        publication=approve_and_publish(repo,w,i,r)
        snapshot=repo.create_publication_snapshot(publication['publication_id'],report_id=report['report_id'],actor='publisher')
        assert snapshot['snapshot']['snapshot_version']=='1.8.0' and snapshot['report_hash']==report['content_hash']
        one=repo.build_reproducible_export(workspace_id=w,initiative_id=i,report_id=report['report_id'],publication_snapshot_id=snapshot['snapshot_id'],destination=path1)
        two=repo.build_reproducible_export(workspace_id=w,initiative_id=i,report_id=report['report_id'],publication_snapshot_id=snapshot['snapshot_id'],destination=path2)
        assert one['archive_hash']==two['archive_hash'] and path1.read_bytes()==path2.read_bytes()
        verified=repo.verify_reproducible_export(path1)
        assert verified['valid'] and verified['manifest']['bundle_version']=='1.8.0'
        assert one['artifact_count']>=8

def test_snapshot_requires_published_publication(tmp_path):
    with SQLiteImpactRepository(tmp_path/'gate.sqlite3') as repo:
        _,w,i,r=create(repo)
        draft=repo.create_publication({'subject_type':'contract','subject_id':r,'title':'Draft'},workspace_id=w,initiative_id=i)
        with pytest.raises(ReportingError,match='published publication'): repo.create_publication_snapshot(draft['publication_id'])

def test_reporting_schema_and_workspace_restore(tmp_path):
    export_path = tmp_path / 'restorable-export.zip'
    with SQLiteImpactRepository(tmp_path/'source.sqlite3') as source:
        _,w,i,r=create(source)
        source.register_report_template({'name':'Default report'},workspace_id=w)
        report=source.create_report({'title':'Restorable report'},workspace_id=w,initiative_id=i)
        dash=source.create_dashboard({'name':'Restorable dashboard'},workspace_id=w,initiative_id=i)
        source.add_dashboard_card(dash['dashboard_id'],{'card_type':'narrative','title':'Summary','alt_text':'Narrative summary','configuration':{'text':'Governed summary.'}})
        publication=approve_and_publish(source,w,i,r)
        snapshot=source.create_publication_snapshot(publication['publication_id'],report_id=report['report_id'])
        source.build_reproducible_export(workspace_id=w,initiative_id=i,report_id=report['report_id'],publication_snapshot_id=snapshot['snapshot_id'],destination=export_path)
        reporting=source.export_reporting_repository(w); bundle=source.export_workspace_bundle(w)
        Draft202012Validator(json.loads((ROOT/'schemas/global_impact_reporting_repository.schema.json').read_text()),format_checker=FormatChecker()).validate(reporting)
        Draft202012Validator(json.loads((ROOT/'schemas/global_impact_workspace_bundle.schema.json').read_text()),format_checker=FormatChecker()).validate(bundle)
        assert reporting['integrity']['valid']
        assert reporting['integrity']['export_bundle_count']==1
        assert bundle['bundle_version']=='1.8.0' and bundle['database_schema_version']==9
    with SQLiteImpactRepository(tmp_path/'target.sqlite3') as target:
        assert target.restore_workspace_bundle(bundle)['status']=='restored'
        assert target.restore_workspace_bundle(bundle)['status']=='unchanged'
        restored=target.export_reporting_repository(w)
        assert restored['integrity']==reporting['integrity']
        assert restored['export_bundles'][0]['archive_hash']==reporting['export_bundles'][0]['archive_hash']
        assert restored['export_bundles'][0]['artifacts']==reporting['export_bundles'][0]['artifacts']
