# Database Migrations

The SQLite repository uses an append-only `schema_migrations` table and five repeatable migrations.

1. **Core repository** — canonical contract snapshots and indexed entity projections.
2. **Portfolios and autosave** — portfolios, memberships, and recoverable draft autosaves.
3. **Imports, audit, and bundles** — idempotent import receipts, audit history, and workspace-restore receipts.
4. **Sources, provenance, and evidence** — source records, immutable source versions, evidence, datasets, provenance edges, and claim-evidence links.
5. **Indicator registry, units, baselines, targets, and methods** — governed units, versioned definitions and models, and initiative-indicator bindings.

The executable SQL is embedded in `python/global_impact_repository.py` so the standard-library package remains portable. Human-readable migration inventory files are retained under `migrations/` for release inspection.

## Rules

- Migrations run in ascending order.
- An applied migration is never rerun.
- The repository can be initialized to any supported migration version and upgraded to the latest version.
- Downgrades are not performed automatically.
- Unknown future versions are rejected rather than guessed.
- Seed data is idempotent and does not overwrite workspace-specific records.

## Verification

`tests/test_repository.py` creates databases at supported prior versions, reruns migrations to prove idempotence, and upgrades each state to schema 5. `tests/test_indicator_registry.py` verifies standard-unit seeding, automatic contract materialization, registry export, and lossless restore.

## Migration 004 — Sources, provenance, and evidence

Adds source records, immutable source versions, evidence items, datasets, provenance edges, and claim-evidence links. Existing v1.2.0 databases migrate in place without changing canonical contract snapshots.

## Migration 005 — Indicator registry, units, baselines, targets, and methods

Adds standard and custom units; indicator definitions and immutable versions; baseline, target, and method records and versions; and stable indicator-registry bindings. Existing v1.3.0 databases migrate in place. Saving or importing a contract materializes registry objects without changing the contract’s v1.1.0 calculation output.
