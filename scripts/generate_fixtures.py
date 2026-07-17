#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from python.global_impact_core import build_impact_contract, input_from_dict
OUT = ROOT / 'contracts/fixtures'
STAMP = '2026-07-17T18:00:00+00:00'
BASE = {
    'workspace':'Community Impact Portfolio','initiative':'Community Energy Retrofit Pilot',
    'goal':'Reduce household energy burden while improving residential efficiency.',
    'outcome':'Participating households experience lower monthly energy costs.',
    'sdg_theme':'Affordable and clean energy','indicator':'Average monthly bill reduction',
    'indicator_definition':'Mean reduction in monthly household utility bills relative to the baseline period.',
    'unit':'USD','baseline_value':0,'current_value':18,'target_value':30,
    'baseline_period':'2025 baseline','current_period':'2026 Q2','target_period':'2027',
    'source':'Pilot utility-billing sample and participant survey summary',
    'source_locator':'Internal pilot evidence package GIC-ENERGY-2026-Q2',
    'method_name':'Before-and-after billing comparison','method_version':'1.0','design_type':'before_after',
    'method_notes':'Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.',
    'confidence':'medium','review_status':'needs_review','beneficiaries':420,
    'population_group':'Participating households','geography':'Chicago, Illinois',
    'budget_usd':125000,'budget_currency':'USD','higher_is_better':True,
    'claim_type':'progress_to_target_statement','claim_statement':''
}
CASES = {
 '01-progress-contract':{},
 '02-lower-is-better':{'indicator':'Average monthly energy use','indicator_definition':'Mean monthly household electricity use.','unit':'kWh','baseline_value':100,'current_value':70,'target_value':50,'higher_is_better':'false'},
 '03-zero-baseline':{'baseline_value':0,'current_value':5,'target_value':10},
 '04-equal-baseline-target':{'baseline_value':10,'current_value':10,'target_value':10},
 '05-period-order-error':{'baseline_period':'2027','current_period':'2026 Q2'},
 '06-unit-mismatch':{'baseline_unit':'USD','current_unit':'EUR','target_unit':'USD'},
 '07-comparison-blocked':{'claim_type':'comparison','claim_statement':'Participants improved more than nonparticipants.','design_type':'before_after','comparison_basis':''},
 '08-comparison-eligible':{'claim_type':'comparison','claim_statement':'Participants improved more than the matched comparison group.','design_type':'comparison_group','comparison_basis':'Matched nonparticipant households'},
 '09-contribution-blocked':{'claim_type':'contribution_statement','claim_statement':'The pilot contributed to lower bills.','design_type':'monitoring','contribution_rationale':''},
 '10-causal-blocked':{'claim_type':'causal_claim','claim_statement':'The pilot caused the observed bill reduction.','design_type':'before_after','confidence':'medium','review_status':'draft'},
 '11-causal-eligible':{'claim_type':'causal_claim','claim_statement':'Assignment to the retrofit pilot caused a reduction in monthly bills.','design_type':'randomized','causal_design':'Random assignment with prespecified intent-to-treat analysis and documented attrition checks.','confidence':'high','review_status':'reviewed'},
 '12-published-with-budget':{'review_status':'published','confidence':'high','current_value':35},
 '13-blank-required-facts':{'initiative':'','goal':'','indicator':'','unit':'','baseline_period':'','current_period':'','source':'','source_locator':'','method_notes':''},
 '14-absent-optionals':{'beneficiaries':None,'budget_usd':None,'geography':'Not specified'},
 '15-descriptive-observation':{'claim_type':'descriptive_observation','target_value':30},
}
OUT.mkdir(parents=True, exist_ok=True)
for old in OUT.glob('*.json'): old.unlink()
for name, changes in CASES.items():
    payload={**BASE,**changes}
    expected=build_impact_contract(input_from_dict(payload),generated_at=STAMP)
    (OUT/f'{name}.json').write_text(json.dumps({'name':name,'generated_at':STAMP,'input':payload,'expected':expected},indent=2,ensure_ascii=False)+'\n')
print(f'Generated {len(CASES)} canonical v1.1.0 fixtures.')
