# Global Impact Catalyst

## v2.0.0 — Connected Public-Interest Impact Intelligence Platform

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, sourcing, measuring, reviewing, analyzing, reporting, publishing, exchanging, and governing impact intelligence.

v2.0.0 consolidates the complete v1.x foundation into a connected institutional platform without rewriting or weakening the governed repositories beneath it. It adds:

- institutional records, memberships, roles, permissions, and workspace relationships;
- verified connections to Sustainable Catalyst products and external services;
- evidence-to-decision pathway graphs;
- deterministic multi-step platform workflows and execution histories;
- immutable cross-repository snapshots bound to source hashes;
- correlated platform events and institution-level integrity views;
- unified platform repository export and lossless restore; and
- an authenticated WordPress Connected Impact Platform Hub.

The platform coordinates governed records. It does not convert evidence into automatic truth, causal proof, certification, regulatory compliance, audit assurance, or institutional endorsement.

## Compatibility identities

```text
Package and WordPress plugin: 2.0.0
Database schema:              12
Workspace bundle:             2.0.0
Platform repository:         2.0.0
Production repository:       1.10.0
Integration repository:      1.9.0
Public API:                   v1
Reporting repository:        1.8.0
Analysis repository:         1.7.0
Review workflow:             1.6.0
Measurement repository:      1.5.0
Indicator registry:          1.4.0
Evidence repository:         1.3.0
Canonical contract:          1.1.0
Formula language:            gic-expression-1.0
```

## Architecture

```text
compact authoring input
        ↓
canonical v1.1.0 contract + validation engine
        ↓
SQLite application repository
        ├── initiatives, portfolios, autosaves, imports, and audit history
        ├── sources, versions, evidence, datasets, and provenance
        ├── units, indicators, baselines, targets, formulas, and methods
        ├── observations, beneficiaries, finances, results, and outcome portfolios
        ├── assignments, comments, quality, decisions, revisions, and publications
        ├── trends, benchmarks, comparisons, scenarios, uncertainty, and sensitivity
        ├── reports, dashboards, snapshots, manifests, checksums, and export artifacts
        ├── API clients, public views, embeds, handoffs, and integration events
        ├── locales, offline packages, accessibility, security, backup, recovery, and readiness
        └── institutions, memberships, workspace links, connections, pathways, workflows,
            unified snapshots, and correlated platform events
                                      ↓
 workspace bundle / offline package / SQLite backup / reproducible ZIP / API / embed /
 Sustainable Catalyst handoff / institutional workflow / connected platform snapshot
```

## Python quick start

Initialize a repository and create an initiative:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 init
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 create \
  --input data/sample_global_impact_input.json \
  --generated-at 2026-07-18T12:00:00+00:00
```

Register an institution and connect its workspace:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-institution \
  --input institution.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-platform-member \
  --institution-id gic-institution-… --input member.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 link-platform-workspace \
  --institution-id gic-institution-… --workspace-id gic-workspace-…
```

Create a governed platform workflow and snapshot:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-platform-workflow \
  --institution-id gic-institution-… --workspace-id gic-workspace-… --input workflow.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 run-platform-workflow \
  --workflow-id gic-platform-workflow-…

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 platform-snapshot \
  --institution-id gic-institution-… --workspace-id gic-workspace-…
```

Export the unified platform repository or complete workspace:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 platform-repository \
  --workspace-id gic-workspace-… --output outputs/platform-repository.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 export \
  --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
```

## WordPress

Plugin folder:

```text
wordpress/global-impact-catalyst-demo/
```

Authenticated platform and repository shortcodes:

```text
[global_impact_catalyst_platform_hub]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
[global_impact_catalyst_analysis_studio]
[global_impact_catalyst_reporting_studio]
[global_impact_catalyst_integration_hub]
[global_impact_catalyst_production_readiness]
```

Public shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_public_profile publication_id="..."]
[global_impact_catalyst_indicator_view publication_id="..."]
[global_impact_catalyst_report_view publication_id="..."]
[global_impact_catalyst_compact_embed slug="..."]
```

The canonical demo is public and stateless. Repository and platform interfaces require an authenticated user with `edit_posts` capability and use nonce-protected REST routes. Public publication surfaces remain bound to approved, current snapshots.

## Schemas and examples

- `schemas/global_impact_contract.schema.json` — canonical contract v1.1.0
- `schemas/global_impact_evidence_repository.schema.json` — evidence v1.3.0
- `schemas/global_impact_indicator_registry.schema.json` — registry v1.4.0
- `schemas/global_impact_measurement_repository.schema.json` — measurement v1.5.0
- `schemas/global_impact_review_workflow.schema.json` — review v1.6.0
- `schemas/global_impact_analysis_repository.schema.json` — analysis v1.7.0
- `schemas/global_impact_reporting_repository.schema.json` — reporting v1.8.0
- `schemas/global_impact_integration_repository.schema.json` — integration v1.9.0
- `schemas/global_impact_production_repository.schema.json` — production v1.10.0
- `schemas/global_impact_platform_repository.schema.json` — connected platform v2.0.0
- `schemas/global_impact_workspace_bundle.schema.json` — complete workspace bundle v2.0.0
- `examples/example_global_impact_platform_repository.json`
- `examples/example_global_impact_workspace_bundle.json`

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
for asset in wordpress/global-impact-catalyst-demo/assets/*.js; do node --check "$asset"; done
php -l wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

## Repository structure

```text
app/                                  Application-facing service wrapper
contracts/                            Canonical parity and legacy fixtures
data/                                 Compact authoring sample
migrations/                           Twelve versioned SQLite migrations
python/global_impact_core.py          Canonical v1.1.0 engine
python/global_impact_repository.py    SQLite repository and workspace bundles
python/global_impact_platform.py      Institutional platform and orchestration layer
python/global_impact_service.py       Shared application service
schemas/                              Contract and repository JSON Schemas
scripts/gic_repository.py             Repository and platform CLI
wordpress/                            Public demo and authenticated studios
```

## Governance boundary

Global Impact Catalyst improves structure, persistence, traceability, reproducibility, review visibility, interoperability, and institutional coordination. A quality score remains reviewer judgment, not an audit opinion. A publication or platform snapshot proves which governed records and hashes were included. A checksum proves byte identity. Neither proves source truth, regulatory compliance, attribution, causality, certification, or impact assurance.

## License

See `LICENSE`.
