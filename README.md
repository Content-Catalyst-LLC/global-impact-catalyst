# Global Impact Catalyst

## v1.8.0 — Reporting, Publication, and Reproducible Export Studio

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, sourcing, measuring, reviewing, analyzing, reporting, and publishing governed impact records.

v1.8.0 adds:

- versioned report templates;
- accessible HTML and Markdown reports;
- Harvard, APA, and plain citation records;
- methodology and limitations appendices;
- governed dashboards with text alternatives;
- publication snapshots bound to exact repository hashes;
- deterministic ZIP exports with fixed timestamps;
- artifact manifests and SHA-256 checksums;
- export verification;
- reporting-repository export and lossless restore;
- an authenticated WordPress Reporting Studio.

The canonical calculation contract remains v1.1.0. Reporting inherits the limitations and governance status of its source records. It does not constitute assurance, certification, audit, source authentication, causal proof, or a verified forecast.

## Compatibility identities

```text
Package and WordPress plugin: 1.8.0
Database schema:              9
Workspace bundle:             1.8.0
Reporting repository:         1.8.0
Analysis repository:          1.7.0
Review workflow:              1.6.0
Measurement repository:       1.5.0
Indicator registry:           1.4.0
Evidence repository:          1.3.0
Canonical contract:           1.1.0
Formula language:             gic-expression-1.0
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
        └── reports, dashboards, snapshots, manifests, checksums, and export artifacts
                                      ↓
       workspace bundle / SQLite backup / deterministic reproducible ZIP
```

## Python quick start

Initialize a repository and create an initiative:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 init
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 create \
  --input data/sample_global_impact_input.json \
  --generated-at 2026-07-17T18:00:00+00:00
```

Create a report template and report:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-report-template \
  --workspace-id gic-workspace-… --input report-template.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 create-report \
  --workspace-id gic-workspace-… --initiative-id gic-initiative-… --input report.json
```

Create and verify a reproducible export:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 reproducible-export \
  --workspace-id gic-workspace-… \
  --initiative-id gic-initiative-… \
  --report-id gic-report-… \
  --publication-snapshot-id gic-publication-snapshot-… \
  --output outputs/reproducible-impact-release.zip

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 verify-export \
  --input outputs/reproducible-impact-release.zip
```

Export the complete workspace:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 export \
  --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
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
[global_impact_catalyst_review_workflow]
[global_impact_catalyst_analysis_studio]
[global_impact_catalyst_reporting_studio]
```

The canonical demo is public and stateless. Repository interfaces require an authenticated user with `edit_posts` capability and use nonce-protected REST routes.

## Schemas and examples

- `schemas/global_impact_contract.schema.json` — canonical contract v1.1.0
- `schemas/global_impact_evidence_repository.schema.json` — evidence v1.3.0
- `schemas/global_impact_indicator_registry.schema.json` — registry v1.4.0
- `schemas/global_impact_measurement_repository.schema.json` — measurement v1.5.0
- `schemas/global_impact_review_workflow.schema.json` — review v1.6.0
- `schemas/global_impact_analysis_repository.schema.json` — analysis v1.7.0
- `schemas/global_impact_reporting_repository.schema.json` — reporting v1.8.0
- `schemas/global_impact_reproducible_export.schema.json` — reproducible export manifest v1.8.0
- `schemas/global_impact_workspace_bundle.schema.json` — complete workspace bundle v1.8.0
- `examples/example_global_impact_reporting_repository.json`
- `examples/example_global_impact_reproducible_export_manifest.json`
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
migrations/                           Versioned SQLite migrations
python/global_impact_core.py          Canonical v1.1.0 engine
python/global_impact_repository.py    SQLite repository and workspace bundles
python/global_impact_reporting.py     Reports, dashboards, snapshots, and exports
python/global_impact_service.py       Shared application service
schemas/                              Contract and repository JSON Schemas
scripts/gic_repository.py             Repository CLI
wordpress/                            Public demo and authenticated studios
```

## Governance boundary

Global Impact Catalyst improves structure, persistence, traceability, reproducibility, review visibility, and byte-level export integrity. A quality score remains reviewer judgment, not an audit opinion. A publication snapshot proves which governed records were included. A checksum proves byte identity. Neither proves source truth, regulatory compliance, attribution, causality, certification, or impact assurance.

## License

See `LICENSE`.
