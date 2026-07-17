# Database Migrations

The SQLite repository uses an append-only `schema_migrations` table and three repeatable migrations.

1. **Core repository** — canonical contract snapshots and indexed entity projections.
2. **Portfolios and autosave** — portfolios, memberships, and recoverable draft autosaves.
3. **Imports, audit, and bundles** — idempotent import receipts, audit history, and workspace-restore receipts.

The executable SQL is embedded in `python/global_impact_repository.py` so the standard-library package remains portable. Human-readable migration inventory files are retained under `migrations/` for release inspection.

## Rules

- Migrations run in ascending order.
- An applied migration is never rerun.
- The repository can be initialized to any supported migration version and upgraded to the latest version.
- Downgrades are not performed automatically.
- Unknown future versions are rejected rather than guessed.

## Verification

`tests/test_repository.py` creates databases at versions 0, 1, 2, and 3, reruns migrations to prove idempotence, and upgrades each supported prior state to the current schema.
