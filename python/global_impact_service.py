"""Application service layer for Global Impact Catalyst v1.2.0."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

from python.global_impact_core import (
    CONTRACT_TYPE,
    build_impact_contract,
    input_from_dict,
    migrate_legacy_record,
)
from python.global_impact_repository import (
    ImportResult,
    NotFoundError,
    SQLiteImpactRepository,
    content_hash,
    utc_now,
)

SERVICE_VERSION = "1.2.0"


def compact_input_from_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Project a canonical v1.1+ contract back into the compact authoring model."""
    facts = contract["facts"]
    measurement = facts["measurement"]
    definition = facts["indicator"]["definition_version"]
    observation = measurement["observations"][0]
    source = (facts.get("sources") or [{}])[0]
    method = (facts.get("methods") or [{}])[0]
    population = (facts.get("population_groups") or [{}])[0]
    geography = (facts.get("geographies") or [{}])[0]
    budget = (facts.get("budget_records") or [{}])[0]
    claim = (contract.get("derived", {}).get("claims") or [{}])[0]
    design = claim.get("design_metadata") or {}
    return {
        "workspace": facts["workspace"].get("name", ""),
        "initiative": facts["initiative"].get("name", ""),
        "goal": facts["goal"].get("statement", ""),
        "outcome": (facts.get("outcomes") or [{}])[0].get("statement", ""),
        "sdg_theme": facts["goal"].get("sdg_theme", "Sustainable development"),
        "indicator": facts["indicator"].get("name", ""),
        "indicator_definition": definition.get("name", ""),
        "unit": definition.get("unit", ""),
        "baseline_unit": measurement["baseline"].get("unit", definition.get("unit", "")),
        "current_unit": observation.get("unit", definition.get("unit", "")),
        "target_unit": measurement["target"].get("unit", definition.get("unit", "")),
        "baseline_value": measurement["baseline"].get("value", 0),
        "current_value": observation.get("value", 0),
        "target_value": measurement["target"].get("value", 100),
        "baseline_period": measurement["baseline"].get("period", {}).get("label", ""),
        "current_period": observation.get("period", {}).get("label", ""),
        "target_period": measurement["target"].get("period", {}).get("label", ""),
        "source": source.get("title", ""),
        "source_locator": source.get("locator", ""),
        "method_name": method.get("name", "Entered measurement method"),
        "method_notes": method.get("description", ""),
        "method_version": method.get("version", "1.0"),
        "design_type": method.get("design_type", "before_after"),
        "confidence": claim.get("confidence", "medium"),
        "review_status": contract.get("lifecycle_status", "draft"),
        "beneficiaries": population.get("observed_count"),
        "population_group": population.get("name", "Affected population"),
        "geography": geography.get("name", "Not specified"),
        "budget_usd": budget.get("amount"),
        "budget_currency": budget.get("currency", "USD"),
        "higher_is_better": definition.get("direction", "higher_is_better") == "higher_is_better",
        "claim_type": claim.get("claim_type", "progress_to_target_statement"),
        "claim_statement": claim.get("statement", ""),
        "comparison_basis": design.get("comparison_basis", ""),
        "contribution_rationale": design.get("contribution_rationale", ""),
        "causal_design": design.get("causal_design", ""),
        "created_at": contract.get("created_at", ""),
        "updated_at": contract.get("updated_at", ""),
    }


class ImpactApplicationService:
    """Use-case facade shared by command-line, API, and WordPress integrations."""

    def __init__(self, repository: SQLiteImpactRepository):
        self.repository = repository

    def create_initiative(
        self,
        payload: Dict[str, Any],
        *,
        generated_at: Optional[str] = None,
        actor: str = "system",
        allow_invalid: bool = False,
    ) -> Dict[str, Any]:
        contract = build_impact_contract(
            input_from_dict(payload), generated_at=generated_at, strict=not allow_invalid
        )
        self._reuse_workspace_identity(contract)
        stored = self.repository.save_contract(contract, expected_revision=0, actor=actor)
        return {"contract": contract, "repository": self._contract_metadata(stored)}

    def save_initiative(
        self,
        payload_or_contract: Dict[str, Any],
        *,
        expected_revision: int,
        generated_at: Optional[str] = None,
        actor: str = "system",
        allow_invalid: bool = False,
    ) -> Dict[str, Any]:
        if payload_or_contract.get("contract_type") == CONTRACT_TYPE:
            payload = compact_input_from_contract(payload_or_contract)
            payload["record_id"] = payload_or_contract.get("record_id", "")
            payload["created_at"] = payload_or_contract.get("created_at", "")
            payload["updated_at"] = generated_at or utc_now()
            contract = build_impact_contract(input_from_dict(payload), generated_at=generated_at, strict=not allow_invalid)
        else:
            contract = build_impact_contract(input_from_dict(payload_or_contract), generated_at=generated_at, strict=not allow_invalid)
        stored = self.repository.save_contract(contract, expected_revision=expected_revision, actor=actor)
        return {"contract": contract, "repository": self._contract_metadata(stored)}

    def autosave_initiative(
        self, payload_or_contract: Dict[str, Any], *, base_revision: int, generated_at: Optional[str] = None, actor: str = "system"
    ) -> Dict[str, Any]:
        contract = payload_or_contract if payload_or_contract.get("contract_type") == CONTRACT_TYPE else build_impact_contract(
            input_from_dict(payload_or_contract), generated_at=generated_at, strict=False
        )
        result = self.repository.autosave_contract(contract, base_revision=base_revision, actor=actor)
        return {key: value for key, value in result.items() if key != "contract"} | {"contract": contract}

    def import_document(
        self, document: Dict[str, Any], *, generated_at: Optional[str] = None, actor: str = "system", allow_invalid: bool = True
    ) -> ImportResult:
        if document.get("contract_type") == CONTRACT_TYPE:
            version = str(document.get("contract_version") or "")
            if version in {"1.1.0", "1.2.0"}:
                contract = document
            else:
                raise ValueError(f"unsupported canonical contract version: {version}")
        else:
            contract = migrate_legacy_record(document, generated_at=generated_at, strict=not allow_invalid)
        return self.repository.record_import(document, contract, actor=actor)

    def duplicate_initiative(
        self,
        initiative_id: str,
        *,
        new_name: str,
        target_workspace_name: Optional[str] = None,
        generated_at: Optional[str] = None,
        actor: str = "system",
    ) -> Dict[str, Any]:
        original = self.repository.get_contract(initiative_id=initiative_id)["contract"]
        payload = compact_input_from_contract(original)
        payload["initiative"] = new_name.strip()
        if target_workspace_name:
            payload["workspace"] = target_workspace_name.strip()
        payload.pop("record_id", None)
        timestamp = generated_at or utc_now()
        payload["created_at"] = timestamp
        payload["updated_at"] = timestamp
        duplicated = build_impact_contract(input_from_dict(payload), generated_at=timestamp, strict=False)
        if not target_workspace_name:
            duplicated["facts"]["workspace"] = copy.deepcopy(original["facts"]["workspace"])
            duplicated["facts"]["initiative"]["workspace_id"] = original["facts"]["workspace"]["id"]
        else:
            self._reuse_workspace_identity(duplicated)
        stored = self.repository.save_contract(duplicated, expected_revision=0, actor=actor)
        return {"contract": duplicated, "repository": self._contract_metadata(stored), "duplicated_from": initiative_id}

    def list_initiatives(
        self, *, workspace_id: Optional[str] = None, search: str = "", lifecycle_status: Optional[str] = None, include_archived: bool = False
    ) -> list[Dict[str, Any]]:
        return self.repository.list_entities(
            "initiative", workspace_id=workspace_id, search=search,
            lifecycle_status=lifecycle_status, include_archived=include_archived,
        )

    def export_workspace(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        bundle = self.repository.export_workspace_bundle(workspace_id)
        if destination:
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return bundle

    def restore_workspace(self, bundle: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        return self.repository.restore_workspace_bundle(bundle, actor=actor)


    def _reuse_workspace_identity(self, contract: Dict[str, Any]) -> None:
        """Attach new authoring records to an existing exact-name workspace when present."""
        workspace = contract["facts"]["workspace"]
        name = str(workspace.get("name") or "").strip()
        if not name:
            return
        candidates = self.repository.list_entities("workspace", search=name, include_archived=False)
        existing = next((item for item in candidates if item["name"].casefold() == name.casefold()), None)
        if existing:
            contract["facts"]["workspace"] = copy.deepcopy(existing["document"])
            contract["facts"]["initiative"]["workspace_id"] = existing["entity_id"]

    @staticmethod
    def _contract_metadata(stored: Dict[str, Any]) -> Dict[str, Any]:
        return {key: stored[key] for key in (
            "record_id", "workspace_id", "initiative_id", "contract_version", "save_state",
            "lifecycle_status", "revision", "content_hash", "created_at", "updated_at"
        )}
