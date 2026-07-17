#!/usr/bin/env python3
"""Portable end-to-end release smoke tests for Global Impact Catalyst v1.7.0."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(*args: str, **kwargs) -> None:
    env = dict(os.environ)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    subprocess.run(args, cwd=ROOT, check=True, env=env, **kwargs)


def validate(document: dict, schema_name: str) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document))
    if errors:
        raise AssertionError(f"{schema_name}: {[error.message for error in errors]}")


def main() -> int:
    run(sys.executable, "-m", "pytest", "-q")
    run(sys.executable, "scripts/check_contracts.py")

    if shutil.which("node"):
        run("node", "scripts/check_browser_parity.js")
        for asset in (
            "global-impact-catalyst-demo.js", "global-impact-catalyst-workspace.js",
            "global-impact-catalyst-evidence.js", "global-impact-catalyst-registry.js",
            "global-impact-catalyst-measurement.js", "global-impact-catalyst-review.js",
            "global-impact-catalyst-analysis.js",
        ):
            run("node", "--check", f"wordpress/global-impact-catalyst-demo/assets/{asset}")
    else:
        print("INFO: Node unavailable; browser checks skipped.")

    if shutil.which("php"):
        run("php", "-l", "wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php")
        run("php", "scripts/check_wordpress_instances.php")
    else:
        print("INFO: PHP unavailable; WordPress checks skipped.")

    from python.global_impact_repository import SQLiteImpactRepository
    from python.global_impact_service import ImpactApplicationService

    payload = json.loads((ROOT / "data/sample_global_impact_input.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="gic-v170-") as temp:
        directory = Path(temp)
        database = directory / "impact.sqlite3"
        restored_database = directory / "restored.sqlite3"
        backup = directory / "impact-backup.sqlite3"

        with SQLiteImpactRepository(database) as repository:
            service = ImpactApplicationService(repository)
            created = service.create_initiative(payload, generated_at="2026-07-17T18:00:00+00:00", actor="release-smoke")
            contract = created["contract"]
            validate(contract, "global_impact_contract.schema.json")
            assert contract["contract_version"] == "1.1.0"
            assert contract["derived"]["metrics"]["progress_to_target_percent"] == 60.0

            workspace_id = created["repository"]["workspace_id"]
            initiative_id = created["repository"]["initiative_id"]
            indicator_id = contract["facts"]["indicator"]["id"]
            summary = repository.repository_summary()
            assert summary["database_schema_version"] == 8
            assert summary["contracts"] == 1
            assert summary["sources"] == 1
            assert summary["units"] >= 18
            assert summary["impact_results"] == 1
            assert summary["observation_series"] == 1
            assert summary["beneficiary_definitions"] == 1
            assert summary["financial_records"] == 1
            assert summary["workflow_roles"] == 5
            assert summary["workflow_revisions"] == 1

            q3 = service.record_observation({
                "indicator_id": indicator_id, "period_label": "2026 Q3", "value": 21.5,
                "unit_id": "USD", "data_state": "complete",
                "dimensions": {"geography": "Chicago", "program_site": "North"},
                "denominator": {"definition": "Participating households with complete billing records"},
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            service.record_observation({
                "indicator_id": indicator_id, "period_label": "2026 Q4", "data_state": "missing",
                "unit_id": "USD", "notes": "Awaiting extract",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            service.record_observation({
                "indicator_id": indicator_id, "period_label": "2026 Q3", "value": 22.0,
                "unit_id": "USD", "data_state": "revised",
                "revision_of_observation_id": q3["observation_record_id"],
                "dimensions": {"geography": "Chicago", "program_site": "North"},
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            series = service.observation_series(initiative_id, indicator_id)
            assert series["integrity"]["missing_count"] == 1
            assert series["integrity"]["revised_count"] == 1

            beneficiary = service.register_beneficiary_definition({
                "name": "Direct participating households", "reach_type": "direct",
                "counting_method": "unique", "privacy_level": "aggregate_only",
                "overlap_policy": "estimated_overlap",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            service.record_beneficiary_observation(beneficiary["beneficiary_definition_id"], {
                "period_label": "2026 Q3", "observed_count": 100, "overlap_estimate": 5,
                "dimensions": {"geography": "Chicago", "delivery_channel": "in-person"},
            }, actor="release-smoke")
            beneficiary_summary = repository.beneficiary_summary(initiative_id, period_label="2026 Q3")
            assert beneficiary_summary["adjusted_count"] == 95
            validate(beneficiary_summary, "global_impact_beneficiary_summary.schema.json")

            service.record_financial_record({
                "record_type": "expenditure", "funding_source": "City grant",
                "cost_category": "installation", "period_label": "2026 Q3",
                "amount": 10000, "currency": "USD", "reporting_currency": "USD",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            service.record_financial_record({
                "record_type": "expenditure", "funding_source": "Foundation",
                "cost_category": "training", "period_label": "2026 Q3",
                "amount": 1000, "currency": "EUR", "reporting_currency": "USD", "exchange_rate": 1.1,
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            cost = repository.calculate_cost_metric(
                initiative_id, denominator_type="beneficiary",
                denominator_id=beneficiary["beneficiary_definition_id"],
                period_label="2026 Q3", reporting_currency="USD",
            )
            assert cost["numerator"]["value"] == 11100
            assert cost["denominator"]["value"] == 95

            outcome = repository.list_impact_results(initiative_id=initiative_id, result_type="outcome")[0]
            output = repository.register_impact_result({
                "result_type": "output", "name": "Homes retrofitted",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            repository.relate_impact_results(
                output["result_id"], outcome["result_id"], relationship_type="contributes_to",
                contribution_weight=0.7, actor="release-smoke",
            )
            factor = repository.add_external_factor({
                "name": "Mild seasonal temperatures", "direction": "positive",
                "influence_level": "medium", "period_label": "2026 Q3",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            repository.add_contribution_note({
                "impact_result_id": outcome["result_id"],
                "statement": "The program plausibly contributed to lower bills.",
                "contribution_type": "direct", "external_factor_refs": [factor["external_factor_id"]],
                "limitations": "Weather and tariffs also influenced the observation.",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")

            portfolio = service.create_outcome_portfolio({
                "name": "Household cost outcomes", "aggregation_method": "sum", "target_unit": "USD",
                "period_policy": "exact", "overlap_policy": "exclude_unknown_or_overlapping",
                "missing_data_policy": "exclude_and_disclose",
            }, workspace_id=workspace_id, actor="release-smoke")
            repository.add_outcome_portfolio_member(portfolio["outcome_portfolio_id"], {
                "initiative_id": initiative_id, "indicator_id": indicator_id,
                "impact_result_id": outcome["result_id"], "population_scope": "Chicago households",
                "overlap_group": "chicago-households-2026", "denominator_definition": "Unique households",
            }, actor="release-smoke")
            aggregation = service.aggregate_outcome_portfolio(
                portfolio["outcome_portfolio_id"], period_label="2026 Q3", actor="release-smoke"
            )
            assert aggregation["value"] == 22.0
            validate(aggregation, "global_impact_outcome_portfolio_aggregation.schema.json")

            measurement = service.measurement_repository(workspace_id)
            assert measurement["repository_version"] == "1.5.0"
            assert measurement["integrity"]["valid"]
            validate(measurement, "global_impact_measurement_repository.schema.json")

            registry = repository.export_indicator_registry(workspace_id)
            assert registry["registry_version"] == "1.4.0"
            validate(registry, "global_impact_indicator_registry.schema.json")
            evidence = repository.export_evidence_repository(workspace_id)
            assert evidence["repository_version"] == "1.3.0"
            validate(evidence, "global_impact_evidence_repository.schema.json")

            record_id = created["repository"]["record_id"]
            approver_role = next(role for role in repository.list_workflow_roles(workspace_id) if role["metadata"].get("role_key") == "approver")
            assignment = service.create_review_assignment({
                "subject_type": "contract", "subject_id": record_id,
                "reviewer_id": "reviewer@example.org", "role_id": approver_role["role_id"], "priority": "high",
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            comment = service.add_review_comment(assignment["assignment_id"], {
                "author_id": "reviewer@example.org", "body": "Retain the seasonality limitation."
            }, actor="reviewer@example.org")
            service.submit_quality_assessment({
                "assessor_id": "reviewer@example.org",
                "dimensions": [
                    {"key": "evidence", "score": 85, "maximum_score": 100},
                    {"key": "method", "score": 80, "maximum_score": 100},
                    {"key": "traceability", "score": 90, "maximum_score": 100},
                ],
            }, workspace_id=workspace_id, initiative_id=initiative_id, assignment_id=assignment["assignment_id"], actor="reviewer@example.org")
            repository.resolve_review_comment(comment["comment_id"], actor="release-smoke")
            decision = service.record_approval_decision(
                assignment["assignment_id"], "approve", rationale="Approved for publication.",
                reviewer_id="reviewer@example.org", actor="reviewer@example.org",
            )
            publication = service.create_publication({
                "subject_type": "contract", "subject_id": record_id, "title": "Release smoke impact brief"
            }, workspace_id=workspace_id, initiative_id=initiative_id, actor="publisher")
            publication = service.publish(publication["publication_id"], actor="publisher")
            assert publication["approved_decision_id"] == decision["decision_id"]
            workflow = service.review_workflow(workspace_id)
            assert workflow["workflow_version"] == "1.6.0"
            assert workflow["integrity"]["valid"]
            assert workflow["integrity"]["publication_count"] == 1
            validate(workflow, "global_impact_review_workflow.schema.json")


            trend = service.analyze_trend(initiative_id, indicator_id, missing_policy="warn", persist=True, actor="release-smoke")
            assert trend["statistics"]["absolute_change"] == 4.0
            benchmark = service.register_benchmark({"name":"Q3 peer median","indicator_id":indicator_id,"value":20,"unit_id":"USD","period_label":"2026 Q3","geography":"Chicago"}, workspace_id=workspace_id, actor="release-smoke")
            comparison = service.compare_to_benchmark(initiative_id, indicator_id, benchmark["benchmark_id"], period_policy="same_label", observation_geography="Chicago", direction="higher_is_better", persist=True, actor="release-smoke")
            assert comparison["integrity"]["valid"] and comparison["comparison"]["difference"] == 2.0
            uncertainty = service.register_uncertainty_model({"name":"Ten percent planning range","uncertainty_type":"relative","relative_margin_percent":10}, workspace_id=workspace_id, actor="release-smoke")
            assert repository.apply_uncertainty(uncertainty["uncertainty_model_id"],100)["lower"] == 90
            scenario = service.register_scenario({"name":"Linear planning case","indicator_id":indicator_id,"model_type":"linear","periods":3,"unit_id":"USD","parameters":{"period_change":4},"assumptions":["Observed Q3 value is the base"]}, workspace_id=workspace_id, initiative_id=initiative_id, actor="release-smoke")
            scenario_result = service.evaluate_scenario(scenario["scenario_id"], uncertainty_model_id=uncertainty["uncertainty_model_id"], actor="release-smoke")
            assert [point["value"] for point in scenario_result["points"]] == [22.0,26.0,30.0,34.0]
            sensitivity = service.run_sensitivity_analysis(scenario["scenario_id"], {"period_change":[2,6]}, actor="release-smoke")
            assert sensitivity["integrity"]["parameter_count"] == 1
            binding = repository.connection.execute("SELECT target_model_id FROM indicator_registry_bindings WHERE initiative_id=? AND indicator_id=?",(initiative_id,indicator_id)).fetchone()
            target_path = service.compare_observations_to_target(initiative_id, indicator_id, binding["target_model_id"], persist=True, actor="release-smoke")
            assert target_path["integrity"]["valid"]
            analysis_repository = service.analysis_repository(workspace_id)
            assert analysis_repository["repository_version"] == "1.7.0" and analysis_repository["integrity"]["valid"]
            validate(analysis_repository, "global_impact_analysis_repository.schema.json")

            bundle = repository.export_workspace_bundle(workspace_id)
            assert bundle["bundle_version"] == "1.7.0"
            assert bundle["database_schema_version"] == 8
            validate(bundle, "global_impact_workspace_bundle.schema.json")
            repository.backup_database(backup)

        assert backup.exists() and backup.stat().st_size > 0
        with SQLiteImpactRepository(restored_database) as restored:
            result = restored.restore_workspace_bundle(bundle)
            assert result["status"] == "restored"
            assert restored.restore_workspace_bundle(bundle)["status"] == "unchanged"
            restored_measurement = restored.export_measurement_repository(workspace_id)
            assert restored_measurement["integrity"] == measurement["integrity"]
            assert restored.repository_summary()["portfolio_aggregation_runs"] == 1
            restored_workflow = restored.export_review_workflow(workspace_id)
            assert restored_workflow["integrity"] == workflow["integrity"]
            assert restored_workflow["publications"][0]["publication_status"] == "published"
            restored_analysis = restored.export_analysis_repository(workspace_id)
            assert restored_analysis["integrity"] == analysis_repository["integrity"]

    print("Global Impact Catalyst v1.7.0 portable release smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
