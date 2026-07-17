# Global Impact Catalyst

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, sourcing, governing, measuring, and transporting impact records. It combines a canonical impact contract with persistent initiatives, evidence provenance, governed indicator definitions, multi-period observations, aggregate beneficiary records, program finances, and guarded outcome portfolios.

The system is not an ESG assurance platform, certification tool, audit substitute, causal-proof engine, regulatory filing system, or automatic truth system.

## v1.5.0 — Observations, Beneficiaries, Budgets, and Outcome Portfolios

v1.5.0 adds a program-measurement layer around the canonical v1.1.0 contract, the v1.3.0 evidence chain, and the v1.4.0 indicator registry:

- Multi-period observations with complete, missing, late, revised, and partial data states
- Revision links, aggregate disaggregation dimensions, denominator definitions, and source/method references
- Aggregate-only beneficiary definitions for direct, indirect, and combined reach
- Unique, estimated-unique, encounter, household, and organization counting methods
- Explicit overlap assumptions, overlap estimates, and privacy-safe beneficiary summaries
- Budgets, expenditures, commitments, and funding records with cost categories and funding sources
- Explicit exchange rates and reporting currencies rather than silent currency conversion
- Cost-per-output, cost-per-outcome, and cost-per-beneficiary calculations with methodological boundaries
- Output, outcome, and long-term-impact records with typed contribution relationships
- External factors and contribution notes that preserve alternative explanations and limitations
- Outcome portfolios with period, unit, missing-data, and population-overlap guards
- Schema-validated measurement-repository export and lossless workspace restore
- Python service, CLI, and authenticated WordPress measurement workflows

The package, application, database schema, workspace bundle, measurement repository, and WordPress plugin are v1.5.0. The indicator registry remains v1.4.0, the evidence formats remain v1.3.0, and the canonical calculation contract remains v1.1.0. This additive release does not alter the existing canonical metrics or browser/Python parity fixtures.

## Architecture

```text
compact authoring input
        ↓
canonical v1.1.0 contract + validation engine
        ↓
application service
        ↓
SQLite repository / CLI / WordPress repository
        ├── initiatives + autosaves + audit history
        ├── sources + versions + evidence + datasets + provenance
        ├── units + indicators + baselines + targets + methods
        └── results + observations + beneficiaries + finances + outcome portfolios
                                      ↓
 workspace bundle / evidence export / registry export / measurement export / backup
```

Canonical contracts remain complete JSON snapshots. Evidence, registry, and measurement records are additive governed repository objects. Updating an observation creates a revision record; updating a unit, definition, model, or method creates a governed version rather than rewriting the version already bound to an initiative.

## Python repository quick start

Initialize a repository and create an initiative:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 init
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 create \
  --input data/sample_global_impact_input.json \
  --generated-at 2026-07-17T18:00:00+00:00
```

Record a new observation:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-observation \
  --workspace-id gic-workspace-… \
  --initiative-id gic-initiative-… \
  --input observation.json
```

Register aggregate beneficiaries and financial records:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-beneficiary-definition \
  --workspace-id gic-workspace-… --initiative-id gic-initiative-… --input beneficiary-definition.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-beneficiary-observation \
  --definition-id gic-beneficiary-… --input beneficiary-observation.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-financial-record \
  --workspace-id gic-workspace-… --initiative-id gic-initiative-… --input financial-record.json
```

Create and aggregate an outcome portfolio:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-outcome-portfolio \
  --workspace-id gic-workspace-… --input portfolio.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-outcome-member \
  --portfolio-id gic-outcome-portfolio-… --input member.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 aggregate-outcome-portfolio \
  --portfolio-id gic-outcome-portfolio-… --period-label "2026 Q3"
```

Export the measurement repository or complete workspace bundle:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 measurement-repository \
  --workspace-id gic-workspace-… --output outputs/measurement-repository.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 export \
  --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
```

## Canonical contract CLI

```bash
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_contract.json \
  --markdown outputs/sample_global_impact_brief.md
```

## WordPress

Plugin folder:

```text
wordpress/global-impact-catalyst-demo/
```

Shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
```

The public demo is stateless. The workspace, evidence ledger, indicator registry, and measurement portfolio require an authenticated user with `edit_posts` capability. The measurement interface records observations, aggregate beneficiary counts, financial records, portfolio memberships, and guarded aggregations.

## JSON Schemas and examples

- `schemas/global_impact_contract.schema.json` — canonical contract v1.1.0
- `schemas/global_impact_evidence_chain.schema.json` — evidence chain v1.3.0
- `schemas/global_impact_indicator_registry.schema.json` — indicator registry v1.4.0
- `schemas/global_impact_measurement_repository.schema.json` — measurement repository v1.5.0
- `schemas/global_impact_outcome_portfolio_aggregation.schema.json` — guarded aggregation v1.5.0
- `schemas/global_impact_beneficiary_summary.schema.json` — aggregate reach summary v1.5.0
- `schemas/global_impact_workspace_bundle.schema.json` — complete workspace bundle v1.5.0
- `examples/example_global_impact_measurement_repository.json`
- `examples/example_global_impact_outcome_portfolio_aggregation.json`
- `examples/example_global_impact_workspace_bundle.json`

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
node --check wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-measurement.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

## Repository structure

```text
app/                                  Application-facing service wrapper
contracts/                            Canonical fixtures and legacy imports
data/                                 Compact authoring sample
docs/                                 Contract, evidence, registry, measurement, and WordPress docs
examples/                             Contract, evidence, registry, measurement, and workspace examples
migrations/                           Versioned SQLite migrations
python/global_impact_core.py          Canonical v1.1.0 engine
python/global_impact_repository.py    SQLite repository and workspace bundles
python/global_impact_registry.py      Units, indicators, baselines, targets, and methods
python/global_impact_measurement.py   Observations, beneficiaries, finances, results, and portfolios
python/global_impact_service.py       Shared application service
schemas/                              Contract and repository JSON Schemas
scripts/gic_repository.py             Repository CLI
wordpress/                            Demo and authenticated repository interfaces
```

## Methodological and privacy boundary

Global Impact Catalyst improves structure, persistence, integrity signals, reproducibility, and review visibility. A unit conversion demonstrates numerical compatibility under registered rules; it does not establish methodological comparability. A cost metric is a transparent ratio under declared records and denominators; it is not proof of efficiency or value for money. A portfolio aggregation combines compatible recorded observations; it does not prove attribution or eliminate double counting beyond its disclosed rules. Core beneficiary workflows store aggregate counts and dimensions, not individual beneficiary records or direct identifiers.

## License

See `LICENSE`.
