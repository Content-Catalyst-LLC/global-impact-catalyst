from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from python.global_impact_measurement import AggregationGuardError, PrivacyBoundaryError
from python.global_impact_repository import DATABASE_SCHEMA_VERSION, SQLiteImpactRepository
from python.global_impact_service import ImpactApplicationService

ROOT = Path(__file__).resolve().parents[1]
FIXED = "2026-07-17T18:00:00+00:00"


def sample_payload():
    return json.loads((ROOT / "data/sample_global_impact_input.json").read_text())


def create(repo: SQLiteImpactRepository):
    return ImpactApplicationService(repo).create_initiative(sample_payload(), generated_at=FIXED)


def ids(created):
    facts = created["contract"]["facts"]
    return created["repository"]["workspace_id"], created["repository"]["initiative_id"], facts["indicator"]["id"]


def test_migration_6_and_contract_materialization(tmp_path):
    with SQLiteImpactRepository(tmp_path / "measurement.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, indicator_id = ids(created)
        assert DATABASE_SCHEMA_VERSION == 9
        assert repo.schema_version == 9
        summary = repo.repository_summary()
        assert summary["impact_results"] == 1
        assert summary["observation_series"] == 1
        assert summary["beneficiary_definitions"] == 1
        assert summary["beneficiary_observations"] == 1
        assert summary["financial_records"] == 1
        series = repo.observation_time_series(initiative_id, indicator_id)
        assert series["observations"][0]["period_label"] == "2026 Q2"
        assert series["observations"][0]["value"] == 18.0
        measurement = repo.export_measurement_repository(workspace_id)
        assert measurement["repository_version"] == "1.5.0"
        assert measurement["integrity"]["valid"] is True


def test_multi_period_observations_states_and_revisions(tmp_path):
    with SQLiteImpactRepository(tmp_path / "series.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, indicator_id = ids(created)
        binding = repo.connection.execute(
            "SELECT * FROM indicator_registry_bindings WHERE initiative_id=? AND indicator_id=?",
            (initiative_id, indicator_id),
        ).fetchone()
        q3 = repo.record_observation({
            "indicator_id": indicator_id, "indicator_definition_id": binding["indicator_definition_id"],
            "period_label": "2026 Q3", "value": 21, "unit_id": "USD",
            "dimensions": {"geography": "Chicago", "program_site": "North"},
            "denominator": {"definition": "Participating households with complete billing records"},
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        repo.record_observation({
            "indicator_id": indicator_id, "period_label": "2026 Q4", "data_state": "missing",
            "unit_id": "USD", "notes": "Utility extract not received",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        revised = repo.record_observation({
            "indicator_id": indicator_id, "period_label": "2026 Q3", "value": 22.5, "unit_id": "USD",
            "data_state": "revised", "revision_of_observation_id": q3["observation_record_id"],
            "dimensions": {"geography": "Chicago", "program_site": "North"},
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        repo.record_observation({
            "indicator_id": indicator_id, "period_label": "2027 Q1", "value": 8, "unit_id": "USD",
            "data_state": "partial",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        series = repo.observation_time_series(initiative_id, indicator_id)
        assert q3["observation_record_id"] not in {item["observation_record_id"] for item in series["observations"]}
        assert revised["observation_record_id"] in {item["observation_record_id"] for item in series["observations"]}
        assert series["integrity"]["missing_count"] == 1
        assert series["integrity"]["partial_count"] == 1
        assert series["integrity"]["revised_count"] == 1


def test_disaggregation_rejects_direct_identifiers(tmp_path):
    with SQLiteImpactRepository(tmp_path / "privacy.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, indicator_id = ids(created)
        with pytest.raises(PrivacyBoundaryError):
            repo.record_observation({
                "indicator_id": indicator_id, "period_label": "2026 Q3", "value": 1, "unit_id": "count",
                "dimensions": {"email": "person@example.com"},
            }, workspace_id=workspace_id, initiative_id=initiative_id)
        definition = repo.register_beneficiary_definition({"name": "Participants"}, workspace_id=workspace_id, initiative_id=initiative_id)
        with pytest.raises(PrivacyBoundaryError):
            repo.record_beneficiary_observation(definition["beneficiary_definition_id"], {
                "period_label": "2026 Q3", "observed_count": 10, "dimensions": {"full_name": "Example Person"},
            })


def test_beneficiary_definitions_reach_overlap_and_privacy_boundary(tmp_path):
    with SQLiteImpactRepository(tmp_path / "beneficiaries.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, _ = ids(created)
        direct = repo.register_beneficiary_definition({
            "name": "Direct participants", "reach_type": "direct", "counting_method": "unique",
            "overlap_policy": "estimated_overlap", "privacy_level": "aggregate_only",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        indirect = repo.register_beneficiary_definition({
            "name": "Household members", "reach_type": "indirect", "counting_method": "estimated_unique",
            "overlap_policy": "estimated_overlap", "privacy_level": "aggregate_only",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        repo.record_beneficiary_observation(direct["beneficiary_definition_id"], {
            "period_label": "2026 Q3", "observed_count": 100, "overlap_estimate": 5,
            "dimensions": {"age_band": "18-64", "delivery_channel": "in-person"},
        })
        repo.record_beneficiary_observation(indirect["beneficiary_definition_id"], {
            "period_label": "2026 Q3", "observed_count": 60, "overlap_estimate": 10,
            "dimensions": {"geography": "Chicago"},
        })
        summary = repo.beneficiary_summary(initiative_id, period_label="2026 Q3")
        assert summary["direct_count"] == 100
        assert summary["indirect_count"] == 60
        assert summary["overlap_deduction"] == 15
        assert summary["adjusted_count"] == 145
        assert "personally identifiable" in summary["privacy_boundary"]


def test_financial_records_reporting_currency_and_cost_metrics(tmp_path):
    with SQLiteImpactRepository(tmp_path / "finance.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, indicator_id = ids(created)
        repo.record_financial_record({
            "record_type": "expenditure", "funding_source": "City grant", "cost_category": "equipment",
            "period_label": "2026 Q3", "amount": 10000, "currency": "USD", "reporting_currency": "USD",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        converted = repo.record_financial_record({
            "record_type": "expenditure", "funding_source": "Foundation", "cost_category": "training",
            "period_label": "2026 Q3", "amount": 1000, "currency": "EUR", "reporting_currency": "USD", "exchange_rate": 1.1,
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        assert converted["reporting_amount"] == 1100
        with pytest.raises(Exception):
            repo.record_financial_record({
                "record_type": "expenditure", "period_label": "2026 Q3", "amount": 100,
                "currency": "EUR", "reporting_currency": "USD",
            }, workspace_id=workspace_id, initiative_id=initiative_id)
        definition = repo.register_beneficiary_definition({
            "name": "Q3 participants", "reach_type": "direct", "counting_method": "unique", "overlap_policy": "no_overlap",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        repo.record_beneficiary_observation(definition["beneficiary_definition_id"], {"period_label": "2026 Q3", "observed_count": 100})
        metric = repo.calculate_cost_metric(
            initiative_id, denominator_type="beneficiary", denominator_id=definition["beneficiary_definition_id"],
            period_label="2026 Q3", reporting_currency="USD",
        )
        assert metric["numerator"]["value"] == 11100
        assert metric["denominator"]["value"] == 100
        assert metric["value"] == 111
        assert "do not establish" in metric["boundary"]
        repo.record_observation({
            "indicator_id": indicator_id, "period_label": "2026 Q3", "value": 50, "unit_id": "count",
            "denominator": {"definition": "Completed retrofit installations"},
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        output_cost = repo.calculate_cost_metric(
            initiative_id, denominator_type="output", denominator_id=indicator_id,
            period_label="2026 Q3", reporting_currency="USD",
        )
        assert output_cost["value"] == 222
        assert output_cost["denominator"]["definition"] == "Completed retrofit installations"


def test_output_outcome_impact_relationships_and_contribution_context(tmp_path):
    with SQLiteImpactRepository(tmp_path / "results.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, _ = ids(created)
        output = repo.register_impact_result({"result_type": "output", "name": "Homes retrofitted"}, workspace_id=workspace_id, initiative_id=initiative_id)
        outcome = repo.list_impact_results(initiative_id=initiative_id, result_type="outcome")[0]
        impact = repo.register_impact_result({"result_type": "long_term_impact", "name": "Lower community energy burden"}, workspace_id=workspace_id, initiative_id=initiative_id)
        first = repo.relate_impact_results(output["result_id"], outcome["result_id"], relationship_type="contributes_to", contribution_weight=0.7)
        second = repo.relate_impact_results(outcome["result_id"], impact["result_id"], relationship_type="enables")
        factor = repo.add_external_factor({
            "name": "Unusually mild winter", "direction": "positive", "influence_level": "high", "period_label": "2026 Q3",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        note = repo.add_contribution_note({
            "impact_result_id": outcome["result_id"], "statement": "The retrofit program plausibly contributed to lower bills.",
            "contribution_type": "direct", "external_factor_refs": [factor["external_factor_id"]],
            "limitations": "Weather and tariff changes also affected bills.",
        }, workspace_id=workspace_id, initiative_id=initiative_id)
        assert first["contribution_weight"] == 0.7
        assert second["relationship_type"] == "enables"
        assert note["external_factor_refs"] == [factor["external_factor_id"]]


def test_outcome_portfolio_aggregation_rules_exclusions_and_overlap(tmp_path):
    with SQLiteImpactRepository(tmp_path / "portfolio.sqlite3") as repo:
        first = create(repo)
        service = ImpactApplicationService(repo)
        second = service.duplicate_initiative(first["repository"]["initiative_id"], new_name="Second initiative", generated_at="2026-07-18T00:00:00+00:00")
        workspace_id, first_id, indicator_id = ids(first)
        second_id = second["repository"]["initiative_id"]
        second_indicator = second["contract"]["facts"]["indicator"]["id"]
        repo.record_observation({"indicator_id": indicator_id, "period_label": "2026 Q3", "value": 10, "unit_id": "count"}, workspace_id=workspace_id, initiative_id=first_id)
        repo.record_observation({"indicator_id": second_indicator, "period_label": "2026 Q3", "value": 20, "unit_id": "count"}, workspace_id=workspace_id, initiative_id=second_id)
        portfolio = repo.create_outcome_portfolio({
            "name": "Retrofit outputs", "aggregation_method": "sum", "target_unit": "count",
            "period_policy": "exact", "overlap_policy": "exclude_unknown_or_overlapping",
        }, workspace_id=workspace_id)
        repo.add_outcome_portfolio_member(portfolio["outcome_portfolio_id"], {
            "initiative_id": first_id, "indicator_id": indicator_id, "population_scope": "Chicago households",
            "overlap_group": "households-2026", "denominator_definition": "Unique households",
        })
        repo.add_outcome_portfolio_member(portfolio["outcome_portfolio_id"], {
            "initiative_id": second_id, "indicator_id": second_indicator, "population_scope": "Chicago households",
            "overlap_group": "households-2026", "denominator_definition": "Unique households",
        })
        result = repo.aggregate_outcome_portfolio(portfolio["outcome_portfolio_id"], period_label="2026 Q3")
        assert result["value"] == 10
        assert result["integrity"]["included_count"] == 1
        assert result["excluded"][0]["reason"] == "overlapping_population"
        assert result["rules"]["overlap_policy"] == "exclude_unknown_or_overlapping"
        fail = repo.create_outcome_portfolio({
            "name": "Strict outputs", "aggregation_method": "sum", "target_unit": "count",
            "overlap_policy": "fail_on_overlap", "missing_data_policy": "fail_on_missing",
        }, workspace_id=workspace_id)
        for iid, ind in ((first_id, indicator_id), (second_id, second_indicator)):
            repo.add_outcome_portfolio_member(fail["outcome_portfolio_id"], {
                "initiative_id": iid, "indicator_id": ind, "overlap_group": "same", "denominator_definition": "Unique households",
            })
        with pytest.raises(AggregationGuardError):
            repo.aggregate_outcome_portfolio(fail["outcome_portfolio_id"], period_label="2026 Q3")


def test_portfolio_excludes_incompatible_units_and_partial_periods(tmp_path):
    with SQLiteImpactRepository(tmp_path / "guards.sqlite3") as repo:
        created = create(repo)
        workspace_id, initiative_id, indicator_id = ids(created)
        repo.record_observation({"indicator_id": indicator_id, "period_label": "2026 Q3", "value": 5, "unit_id": "kg", "data_state": "partial"}, workspace_id=workspace_id, initiative_id=initiative_id)
        portfolio = repo.create_outcome_portfolio({"name": "Guarded", "target_unit": "USD", "missing_data_policy": "exclude_and_disclose"}, workspace_id=workspace_id)
        repo.add_outcome_portfolio_member(portfolio["outcome_portfolio_id"], {"initiative_id": initiative_id, "indicator_id": indicator_id})
        partial = repo.aggregate_outcome_portfolio(portfolio["outcome_portfolio_id"], period_label="2026 Q3")
        assert partial["value"] is None
        assert partial["excluded"][0]["reason"] == "partial_period_excluded"
        include = repo.create_outcome_portfolio({"name": "Include partial", "target_unit": "USD", "missing_data_policy": "include_partial"}, workspace_id=workspace_id)
        repo.add_outcome_portfolio_member(include["outcome_portfolio_id"], {"initiative_id": initiative_id, "indicator_id": indicator_id})
        incompatible = repo.aggregate_outcome_portfolio(include["outcome_portfolio_id"], period_label="2026 Q3")
        assert incompatible["value"] is None
        assert incompatible["excluded"][0]["reason"] == "incompatible_unit"


def test_measurement_repository_workspace_export_restore_and_schema(tmp_path):
    with SQLiteImpactRepository(tmp_path / "source.sqlite3") as source:
        created = create(source)
        workspace_id, initiative_id, indicator_id = ids(created)
        source.record_observation({"indicator_id": indicator_id, "period_label": "2026 Q3", "value": 20, "unit_id": "USD"}, workspace_id=workspace_id, initiative_id=initiative_id)
        portfolio = source.create_outcome_portfolio({"name": "Outcome view", "target_unit": "USD"}, workspace_id=workspace_id)
        source.add_outcome_portfolio_member(portfolio["outcome_portfolio_id"], {"initiative_id": initiative_id, "indicator_id": indicator_id})
        source.aggregate_outcome_portfolio(portfolio["outcome_portfolio_id"], period_label="2026 Q3")
        bundle = source.export_workspace_bundle(workspace_id)
        measurement = bundle["measurement_repository"]
        schema = json.loads((ROOT / "schemas/global_impact_measurement_repository.schema.json").read_text())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(measurement)
        workspace_schema = json.loads((ROOT / "schemas/global_impact_workspace_bundle.schema.json").read_text())
        Draft202012Validator(workspace_schema, format_checker=FormatChecker()).validate(bundle)
    with SQLiteImpactRepository(tmp_path / "target.sqlite3") as target:
        restored = target.restore_workspace_bundle(bundle)
        repeated = target.restore_workspace_bundle(bundle)
        assert restored["status"] == "restored"
        assert repeated["status"] == "unchanged"
        summary = target.repository_summary()
        assert summary["observation_series"] >= 2
        assert summary["outcome_portfolios"] == 1
        assert summary["portfolio_aggregation_runs"] == 1
        restored_measurement = target.export_measurement_repository(workspace_id)
        assert restored_measurement["integrity"]["valid"] is True
