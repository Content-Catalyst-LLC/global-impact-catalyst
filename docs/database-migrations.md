# Database Migrations

The SQLite repository uses an append-only `schema_migrations` table and twelve repeatable migrations.

1. **Core repository** — canonical contract snapshots and indexed entity projections.
2. **Portfolios and autosave** — portfolios, memberships, and recoverable drafts.
3. **Imports, audit, and bundles** — import receipts, audit history, and restore receipts.
4. **Sources, provenance, and evidence** — sources, immutable versions, evidence, datasets, provenance edges, and claim links.
5. **Indicator registry** — units, definitions, formulas, baselines, targets, methods, and bindings.
6. **Program measurement** — multi-period observations, beneficiaries, finances, result relationships, and outcome portfolios.
7. **Review and publication governance** — roles, assignments, comments, quality, decisions, revisions, corrections, publications, and events.
8. **Analysis repository** — trends, benchmarks, comparison sets, scenarios, uncertainty, sensitivity, and analysis runs.
9. **Reporting and reproducible exports** — templates, reports, dashboards, publication snapshots, export bundles, and stored artifacts.
10. **Public API and handoffs** — scoped clients, keys, access records, embeds, handoffs, and integration events.
11. **Production hardening** — locales, offline packages and changes, accessibility audits, security policies, backups, recovery tests, environments, and readiness checks.
12. **Connected platform** — institutions, memberships, workspace relationships, verified connections, decision pathways, workflows and runs, unified snapshots, and correlated events.

Executable SQL is loaded by `python/global_impact_repository.py`. Human-readable migration files remain under `migrations/` for release inspection.

## Rules

- Migrations run in ascending order and are recorded exactly once.
- Reopening a current database is idempotent.
- Prior supported schemas upgrade in place.
- Downgrades are not performed automatically.
- Unknown future versions are rejected rather than guessed.
- Seed data does not overwrite workspace-specific records.
- Canonical v1.1.0 contract snapshots are not silently recalculated during migration.
- Platform migration does not execute workflows or contact connected services.

## Migration 12 — Connected Public-Interest Impact Intelligence Platform v2.0.0

Migration 12 creates:

- `institutions`;
- `institution_members`;
- `institution_workspaces`;
- `platform_connections`;
- `decision_pathways`;
- `platform_workflows`;
- `platform_workflow_runs`;
- `platform_snapshots`; and
- `platform_events`.

Existing schema 11 databases migrate in place without recalculating canonical contracts or changing v1.3.0–v1.10.0 repository records. Foreign keys preserve institution, workflow, and event relationships. Stable hashes remain the authority for cross-repository snapshot identity.

## Verification

The automated suite initializes databases, applies all twelve migrations, reruns initialization, exercises every repository layer, creates deterministic exports and connected snapshots, and performs workspace backup and lossless restore.
