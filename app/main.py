"""Application-facing wrapper for Global Impact Catalyst v1.1.0."""
from __future__ import annotations
from typing import Optional
from python.global_impact_core import build_impact_contract,input_from_dict,validation_result,validate_input

def build_demo_response(payload:dict,*,generated_at:Optional[str]=None)->dict:
    return build_impact_contract(input_from_dict(payload),generated_at=generated_at)

def validate_demo_payload(payload:dict)->dict:
    return validation_result(validate_input(input_from_dict(payload)))

def healthcheck()->dict:
    return {'status':'ok','module':'global-impact-catalyst','version':'1.1.0','contract_version':'1.1.0'}
