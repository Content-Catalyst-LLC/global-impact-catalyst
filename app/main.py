"""Application-facing services for Global Impact Catalyst v1.4.0."""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from python.global_impact_core import build_impact_contract, input_from_dict, validation_result, validate_input
from python.global_impact_repository import SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService


def build_demo_response(payload: dict, *, generated_at: Optional[str] = None) -> dict:
    return build_impact_contract(input_from_dict(payload), generated_at=generated_at)


def validate_demo_payload(payload: dict) -> dict:
    return validation_result(validate_input(input_from_dict(payload)))


def open_application(database: str | Path = ":memory:") -> ImpactApplicationService:
    return ImpactApplicationService(SQLiteImpactRepository(database))


def healthcheck() -> dict:
    return {
        "status": "ok",
        "module": "global-impact-catalyst",
        "version": "1.4.0",
        "contract_version": "1.1.0",
        "database_schema_version": 5,
        "persistence": "sqlite",
        "evidence_repository": "sources-provenance-evidence",
        "indicator_registry": "units-baselines-targets-methods",
        "indicator_registry_version": "1.4.0",
    }
