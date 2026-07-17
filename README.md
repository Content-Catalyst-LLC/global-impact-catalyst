# Global Impact Catalyst

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, revising, and transporting impact-measurement records. It combines a canonical impact-contract engine with a persistent repository for initiatives, portfolios, measurements, imports, autosaves, audit records, and recovery bundles.

The system is not an ESG assurance platform, certification tool, audit substitute, causal-proof engine, or automatic truth system.

## v1.2.0 — Persistent Initiatives, Portfolios, and Measurement Repository

v1.2.0 adds durable workspaces around the canonical v1.1.0 contract engine:

- SQLite persistence with repeatable schema migrations
- Complete contract snapshots and indexed entity projections
- Workspace and initiative lists, search, filtering, archive, restore, and duplication
- Portfolios and initiative memberships
- Draft autosave and explicit saved revisions
- Optimistic concurrency conflict protection
- Idempotent v1.0.x and v1.1.0 imports with audit records
- Workspace export, restore, and database backup
- Shared application service and repository CLI
- Authenticated persistent WordPress workspace

Persistence does not change calculation results. The package and repository release are v1.2.0; the canonical contract and calculation schema remain v1.1.0.

## Architecture

```text
compact authoring input
        ↓
canonical v1.1.0 contract + validation engine
        ↓
application service
        ↓
SQLite repository / application wrapper / repository CLI
        ↓
workspaces, initiatives, portfolios, autosaves, imports, audit, bundles
```

Canonical contracts remain complete JSON snapshots. Indexed projections support operational queries without splitting or silently recalculating the source record.

## Python repository quick start

Initialize a local repository:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  init
```

Create and save an initiative:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  create \
  --input data/sample_global_impact_input.json \
  --generated-at 2026-07-17T18:00:00+00:00
```

List or search initiatives:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 list --search energy
```

Import a v1.0.x flat record or v1.1.0 canonical contract:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  import --input contracts/legacy/legacy-v1.0.1-record.json
```

Export a workspace bundle:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  export --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
```

## Canonical contract CLI

The original strict generator remains available:

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
```

The public demo is stateless. The workspace requires authenticated editing access and supports saved records, autosave recovery, search, duplicate, archive/restore, import, and export.

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
node --check wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-workspace.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

## Repository structure

```text
app/                         Application-facing service wrapper
contracts/                   Canonical fixtures and legacy import records
data/                        Compact authoring sample
docs/                        Contract, persistence, migration, bundle, and WordPress docs
examples/                    Canonical contract, brief, and workspace bundle examples
migrations/                  Human-readable database migration inventory
python/global_impact_core.py Canonical v1.1.0 engine
python/global_impact_repository.py  SQLite repository
python/global_impact_service.py     Shared application service
schemas/                     Contract and workspace-bundle schemas
scripts/gic_repository.py    Persistent repository CLI
tests/                       Engine, schema, parity, repository, and integration tests
wordpress/                   Demo and persistent workspace plugin
```

## Methodological boundary

Global Impact Catalyst improves structure, persistence, reproducibility, and review visibility. It does not prove that entered data is accurate, that evidence is authentic, that a method is appropriate, that an intervention caused an outcome, or that a public claim satisfies legal, accounting, evaluation, regulatory, or assurance requirements.

## License

See `LICENSE`.
