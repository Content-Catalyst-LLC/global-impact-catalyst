"""Application service layer for Global Impact Catalyst v1.9.0."""
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

SERVICE_VERSION = "1.9.0"


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


    def register_source(self, source: Dict[str, Any], *, workspace_id: str, initiative_id: Optional[str] = None, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_source(source, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def add_source_version(self, source_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.add_source_version(source_id, **kwargs)

    def capture_evidence(self, source_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.capture_evidence(source_id, **kwargs)

    def register_dataset(self, source_id: str, dataset: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_dataset(source_id, dataset, actor=actor)

    def link_claim_evidence(self, claim_id: str, evidence_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.link_claim_evidence(claim_id, evidence_id, **kwargs)

    def evidence_chain(self, initiative_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        chain = self.repository.evidence_chain(initiative_id)
        if destination:
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(chain, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return chain

    def register_unit(self, unit: Dict[str, Any], *, workspace_id: Optional[str] = None, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_unit(unit, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def register_indicator_definition(self, definition: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_indicator_definition(definition, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def register_baseline_model(self, model: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_baseline_model(model, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def register_target_model(self, model: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_target_model(model, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def register_method_definition(self, method: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_method_definition(method, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def indicator_registry(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        registry = self.repository.export_indicator_registry(workspace_id)
        if destination:
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return registry


    def register_impact_result(self, result: Dict[str, Any], *, workspace_id: str, initiative_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_impact_result(result, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def record_observation(self, observation: Dict[str, Any], *, workspace_id: str, initiative_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.record_observation(observation, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def observation_series(self, initiative_id: str, indicator_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        series = self.repository.observation_time_series(initiative_id, indicator_id)
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(series, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return series

    def register_beneficiary_definition(self, definition: Dict[str, Any], *, workspace_id: str, initiative_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_beneficiary_definition(definition, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def record_beneficiary_observation(self, definition_id: str, observation: Dict[str, Any], *, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.record_beneficiary_observation(definition_id, observation, expected_revision=expected_revision, actor=actor)

    def record_financial_record(self, record: Dict[str, Any], *, workspace_id: str, initiative_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.record_financial_record(record, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def create_outcome_portfolio(self, portfolio: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_outcome_portfolio(portfolio, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def aggregate_outcome_portfolio(self, portfolio_id: str, *, period_start: Optional[str] = None, period_end: Optional[str] = None, period_label: str = "", actor: str = "system") -> Dict[str, Any]:
        return self.repository.aggregate_outcome_portfolio(portfolio_id, period_start=period_start, period_end=period_end, period_label=period_label, actor=actor)

    def measurement_repository(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        measurement = self.repository.export_measurement_repository(workspace_id)
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(measurement, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return measurement


    def register_workflow_role(self, role: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_workflow_role(role, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def create_review_assignment(self, assignment: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_review_assignment(assignment, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)

    def add_review_comment(self, assignment_id: str, comment: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        return self.repository.add_review_comment(assignment_id, comment, actor=actor)

    def submit_quality_assessment(self, assessment: Dict[str, Any], *, workspace_id: str, initiative_id: str, assignment_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.submit_quality_assessment(assessment, workspace_id=workspace_id, initiative_id=initiative_id, assignment_id=assignment_id, actor=actor)

    def record_approval_decision(self, assignment_id: str, decision: str, *, rationale: str, conditions: Optional[list[Any]] = None, reviewer_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.record_approval_decision(assignment_id, decision, rationale=rationale, conditions=conditions, reviewer_id=reviewer_id, actor=actor)

    def open_correction(self, correction: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system") -> Dict[str, Any]:
        return self.repository.open_correction(correction, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)

    def create_publication(self, publication: Dict[str, Any], *, workspace_id: str, initiative_id: str, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_publication(publication, workspace_id=workspace_id, initiative_id=initiative_id, actor=actor)

    def publish(self, publication_id: str, *, actor: str = "system", quality_threshold: float = 60.0) -> Dict[str, Any]:
        return self.repository.publish(publication_id, actor=actor, quality_threshold=quality_threshold)

    def withdraw_publication(self, publication_id: str, *, reason: str, actor: str = "system") -> Dict[str, Any]:
        return self.repository.withdraw_publication(publication_id, reason=reason, actor=actor)

    def review_workflow(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        workflow = self.repository.export_review_workflow(workspace_id)
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return workflow

    def analyze_trend(self, initiative_id: str, indicator_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.analyze_trend(initiative_id, indicator_id, **kwargs)

    def register_benchmark(self, benchmark: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_benchmark(benchmark, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def compare_to_benchmark(self, initiative_id: str, indicator_id: str, benchmark_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.compare_to_benchmark(initiative_id, indicator_id, benchmark_id, **kwargs)

    def create_comparison_set(self, comparison_set: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_comparison_set(comparison_set, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def add_comparison_member(self, comparison_set_id: str, member: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        return self.repository.add_comparison_member(comparison_set_id, member, actor=actor)

    def run_comparison_set(self, comparison_set_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.run_comparison_set(comparison_set_id, **kwargs)

    def register_uncertainty_model(self, model: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_uncertainty_model(model, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def register_scenario(self, scenario: Dict[str, Any], *, workspace_id: str, initiative_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_scenario(scenario, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def evaluate_scenario(self, scenario_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.evaluate_scenario(scenario_id, **kwargs)

    def run_sensitivity_analysis(self, scenario_id: str, parameter_ranges: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        return self.repository.run_sensitivity_analysis(scenario_id, parameter_ranges, **kwargs)

    def compare_observations_to_target(self, initiative_id: str, indicator_id: str, target_model_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.compare_observations_to_target(initiative_id, indicator_id, target_model_id, **kwargs)

    def analysis_repository(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        analysis = self.repository.export_analysis_repository(workspace_id)
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return analysis

    def register_report_template(self, template: Dict[str, Any], *, workspace_id: str, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.register_report_template(template, workspace_id=workspace_id, expected_revision=expected_revision, actor=actor)

    def create_report(self, report: Dict[str, Any], *, workspace_id: str, initiative_id: str, template_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_report(report, workspace_id=workspace_id, initiative_id=initiative_id, template_id=template_id, actor=actor)

    def create_dashboard(self, dashboard: Dict[str, Any], *, workspace_id: str, initiative_id: Optional[str] = None, expected_revision: Optional[int] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_dashboard(dashboard, workspace_id=workspace_id, initiative_id=initiative_id, expected_revision=expected_revision, actor=actor)

    def add_dashboard_card(self, dashboard_id: str, card: Dict[str, Any], *, actor: str = "system") -> Dict[str, Any]:
        return self.repository.add_dashboard_card(dashboard_id, card, actor=actor)

    def create_publication_snapshot(self, publication_id: str, *, report_id: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.create_publication_snapshot(publication_id, report_id=report_id, actor=actor)

    def build_reproducible_export(self, *, workspace_id: str, initiative_id: Optional[str] = None, report_id: Optional[str] = None, publication_snapshot_id: Optional[str] = None, destination: Optional[str | Path] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.build_reproducible_export(workspace_id=workspace_id, initiative_id=initiative_id, report_id=report_id, publication_snapshot_id=publication_snapshot_id, destination=destination, actor=actor)

    def reporting_repository(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        reporting = self.repository.export_reporting_repository(workspace_id)
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(reporting, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return reporting

    def register_api_client(self, client: Dict[str, Any], *, workspace_id: Optional[str] = None, actor: str = "system", issue_key: bool = True) -> Dict[str, Any]:
        return self.repository.register_api_client(client, workspace_id=workspace_id, actor=actor, issue_key=issue_key)

    def issue_api_key(self, client_id: str, *, scopes: list[str], expires_at: Optional[str] = None, actor: str = "system") -> Dict[str, Any]:
        return self.repository.issue_api_key(client_id, scopes=scopes, expires_at=expires_at, actor=actor)

    def public_catalog(self, **kwargs: Any) -> Dict[str, Any]:
        return self.repository.public_catalog(**kwargs)

    def public_publication(self, publication_id: str) -> Dict[str, Any]:
        return self.repository.public_publication(publication_id)

    def workspace_api_resource(self, *, api_key: str, workspace_id: str, resource: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        return self.repository.workspace_api_resource(api_key=api_key, workspace_id=workspace_id, resource=resource, page=page, page_size=page_size)

    def create_embed(self, embed: Dict[str, Any], *, workspace_id: str, actor: str = "system", expected_revision: Optional[int] = None) -> Dict[str, Any]:
        return self.repository.create_embed(embed, workspace_id=workspace_id, actor=actor, expected_revision=expected_revision)

    def render_embed(self, embed_id_or_slug: str) -> Dict[str, Any]:
        return self.repository.render_embed(embed_id_or_slug)

    def create_platform_handoff(self, destination: str, *, workspace_id: str, initiative_id: Optional[str] = None, idempotency_key: Optional[str] = None, actor: str = "system", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.repository.create_platform_handoff(destination, workspace_id=workspace_id, initiative_id=initiative_id, idempotency_key=idempotency_key, actor=actor, metadata=metadata)

    def integration_repository(self, workspace_id: str, destination: Optional[str | Path] = None) -> Dict[str, Any]:
        integration = self.repository.export_integration_repository(workspace_id)
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(integration, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return integration

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
