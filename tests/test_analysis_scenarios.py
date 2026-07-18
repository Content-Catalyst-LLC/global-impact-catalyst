from __future__ import annotations
import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator, FormatChecker
from python.global_impact_analysis import AnalysisError
from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService

ROOT=Path(__file__).resolve().parents[1]
FIXED='2026-07-17T18:00:00+00:00'

def payload(): return json.loads((ROOT/'data/sample_global_impact_input.json').read_text())
def create(repo): return ImpactApplicationService(repo).create_initiative(payload(),generated_at=FIXED)
def ids(created):
    f=created['contract']['facts']; return created['repository']['workspace_id'],created['repository']['initiative_id'],f['indicator']['id']
def binding(repo,initiative_id,indicator_id):
    return dict(repo.connection.execute('SELECT * FROM indicator_registry_bindings WHERE initiative_id=? AND indicator_id=?',(initiative_id,indicator_id)).fetchone())
def add_periods(repo,w,i,indicator):
    for label,value,state in [('2026 Q3',21,'complete'),('2026 Q4',24,'complete'),('2027 Q1',26,'partial')]:
        repo.record_observation({'indicator_id':indicator,'period_label':label,'value':value,'unit_id':'USD','data_state':state,'dimensions':{'geography':'Chicago','population_group':'households'}},workspace_id=w,initiative_id=i)

def validate(path,document):
    schema=json.loads(path.read_text()); errors=list(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(document)); assert not errors,[e.message for e in errors]

def test_migration_and_trend(tmp_path):
    with SQLiteImpactRepository(tmp_path/'a.sqlite3') as repo:
        c=create(repo); w,i,ind=ids(c); add_periods(repo,w,i,ind)
        assert DATABASE_SCHEMA_VERSION==12 and repo.schema_version==12
        result=repo.analyze_trend(i,ind,include_partial=False,persist=True)
        assert [p['value'] for p in result['points']]==[18.0,21.0,24.0]
        assert result['statistics']['absolute_change']==6.0
        assert result['statistics']['percent_change']==pytest.approx(33.333333)
        assert result['statistics']['direction']=='increasing'
        assert len(result['excluded'])==1 and result['analysis_run_id']

def test_benchmark_and_comparison_guards(tmp_path):
    with SQLiteImpactRepository(tmp_path/'b.sqlite3') as repo:
        c=create(repo); w,i,ind=ids(c)
        bench=repo.register_benchmark({'name':'Peer median','indicator_id':ind,'value':20,'unit_id':'USD','period_label':'2026 Q2','geography':'Chicago','population':'households','quality_status':'strong'},workspace_id=w)
        good=repo.compare_to_benchmark(i,ind,bench['benchmark_id'],observation_geography='Chicago',observation_population='households',direction='higher_is_better')
        assert good['comparison']['difference']==-2 and good['comparison']['relation']=='below' and good['comparison']['favorable'] is False
        bad=repo.compare_to_benchmark(i,ind,bench['benchmark_id'],observation_geography='Detroit',geography_policy='exact')
        assert bad['integrity']['valid'] is False and any('geography differs' in x for x in bad['integrity']['blockers'])

def test_comparison_set_rankings(tmp_path):
    with SQLiteImpactRepository(tmp_path/'c.sqlite3') as repo:
        c=create(repo); w,i,ind=ids(c)
        bench=repo.register_benchmark({'name':'Reference','indicator_id':ind,'value':25,'unit_id':'USD'},workspace_id=w)
        cs=repo.create_comparison_set({'name':'Peer view','indicator_id':ind,'comparison_policy':{'period_policy':'ignore','direction':'higher_is_better'}},workspace_id=w)
        repo.add_comparison_member(cs['comparison_set_id'],{'label':'Reference','benchmark_id':bench['benchmark_id']})
        repo.add_comparison_member(cs['comparison_set_id'],{'label':'Pilot','initiative_id':i})
        result=repo.run_comparison_set(cs['comparison_set_id'],persist=True)
        assert [x['label'] for x in result['members']]==['Reference','Pilot']
        assert result['analysis_run_id']

def test_uncertainty_models(tmp_path):
    with SQLiteImpactRepository(tmp_path/'u.sqlite3') as repo:
        c=create(repo); w,_,_=ids(c)
        rel=repo.register_uncertainty_model({'name':'Ten percent','uncertainty_type':'relative','relative_margin_percent':10},workspace_id=w)
        assert repo.apply_uncertainty(rel['uncertainty_model_id'],100)['lower']==90
        combined=repo.register_uncertainty_model({'name':'Combined','uncertainty_type':'combined','absolute_margin':3,'relative_margin_percent':4},workspace_id=w)
        assert repo.apply_uncertainty(combined['uncertainty_model_id'],100)['margin']==5
        with pytest.raises(AnalysisError): repo.register_uncertainty_model({'name':'Bad bounds','uncertainty_type':'bounds','lower_bound':10,'upper_bound':5},workspace_id=w)

def test_scenario_models_target_and_sensitivity(tmp_path):
    with SQLiteImpactRepository(tmp_path/'s.sqlite3') as repo:
        c=create(repo); w,i,ind=ids(c); b=binding(repo,i,ind)
        linear=repo.register_scenario({'name':'Target path','indicator_id':ind,'model_type':'linear','periods':3,'base_value':18,'unit_id':'USD','parameters':{'period_change':4},'target_model_id':b['target_model_id']},workspace_id=w,initiative_id=i)
        result=repo.evaluate_scenario(linear['scenario_id'])
        assert [p['value'] for p in result['points']]==[18,22,26,30]
        assert result['points'][-1]['target_gap']==0
        compound=repo.register_scenario({'name':'Compound','indicator_id':ind,'model_type':'compound','periods':2,'base_value':100,'unit_id':'USD','parameters':{'growth_rate_percent':10}},workspace_id=w,initiative_id=i)
        assert [p['value'] for p in repo.evaluate_scenario(compound['scenario_id'],persist=False)['points']]==[100,110,121]
        step=repo.register_scenario({'name':'Step','indicator_id':ind,'model_type':'step','periods':3,'base_value':10,'unit_id':'USD','parameters':{'step_period':2,'step_value':20}},workspace_id=w,initiative_id=i)
        assert [p['value'] for p in repo.evaluate_scenario(step['scenario_id'],persist=False)['points']]==[10,10,20,20]
        sensitivity=repo.run_sensitivity_analysis(linear['scenario_id'],{'period_change':[1,5],'ceiling':[15,100]})
        assert sensitivity['parameters'][0]['rank']==1 and {x['parameter_name'] for x in sensitivity['parameters']}=={'period_change','ceiling'}

def test_target_trajectory(tmp_path):
    with SQLiteImpactRepository(tmp_path/'t.sqlite3') as repo:
        c=create(repo); w,i,ind=ids(c); add_periods(repo,w,i,ind); b=binding(repo,i,ind)
        result=repo.compare_observations_to_target(i,ind,b['target_model_id'],persist=True)
        assert result['integrity']['valid'] and len(result['points'])==4
        assert result['points'][-1]['gap']<0 and result['analysis_run_id']

def test_analysis_export_schema_and_restore(tmp_path):
    with SQLiteImpactRepository(tmp_path/'source.sqlite3') as source:
        c=create(source); w,i,ind=ids(c)
        source.register_benchmark({'name':'Reference','indicator_id':ind,'value':20,'unit_id':'USD'},workspace_id=w)
        u=source.register_uncertainty_model({'name':'Range','uncertainty_type':'relative','relative_margin_percent':10},workspace_id=w)
        s=source.register_scenario({'name':'Plan','indicator_id':ind,'model_type':'linear','periods':2,'base_value':18,'unit_id':'USD','parameters':{'period_change':2}},workspace_id=w,initiative_id=i)
        source.evaluate_scenario(s['scenario_id'],uncertainty_model_id=u['uncertainty_model_id'])
        source.run_sensitivity_analysis(s['scenario_id'],{'period_change':[1,3]})
        analysis=source.export_analysis_repository(w); bundle=source.export_workspace_bundle(w)
        validate(ROOT/'schemas/global_impact_analysis_repository.schema.json',analysis)
        validate(ROOT/'schemas/global_impact_workspace_bundle.schema.json',bundle)
        assert bundle['bundle_version']=='2.0.0' and bundle['database_schema_version']==12
        with SQLiteImpactRepository(tmp_path/'target.sqlite3') as target:
            first=target.restore_workspace_bundle(bundle); second=target.restore_workspace_bundle(bundle)
            assert first['status']=='restored' and second['status']=='unchanged'
            restored=target.export_analysis_repository(w)
            assert restored['integrity']['valid'] and restored['scenarios'][0]['scenario_id']==s['scenario_id']
