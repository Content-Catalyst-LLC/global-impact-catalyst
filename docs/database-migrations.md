# Database Migrations

The SQLite repository uses an append-only `schema_migrations` table and eleven repeatable migrations.

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

Executable SQL is loaded by `python/global_impact_repository.py`. Human-readable migration files remain under `migrations/` for release inspection.

## Rules

- Migrations run in ascending order and are recorded exactly once.
- Reopening a current database is idempotent.
- Prior supported schemas upgrade in place.
- Downgrades are not performed automatically.
- Unknown future versions are rejected rather than guessed.
- Seed data does not overwrite workspace-specific records.
- Canonical v1.1.0 contract snapshots are not silently recalculated during migration.

## Migration 009

Migration 009 adds governed report templates, report documents, dashboard definitions and cards, publication snapshots, export bundles, and export artifacts. Existing v1.7.0 databases migrate to schema 9 without changing evidence, registry, measurement, review, analysis, or canonical calculation semantics.

## Verification

The automated suite initializes prior database states, applies all eleven migrations, reruns initialization, exercises each repository layer, creates deterministic exports, and performs workspace backup and lossless restore.

## Migration 10 — Public API, embeds, and platform handoffs

Creates API client/key, idempotency, rate-window, access-log, embed-definition, platform-handoff, and integration-event tables. Plaintext API keys are never persisted. The migration is repeatable and upgrades v1.8.0 schema 9 databases to schema 10.


## Migration 11 — Accessibility, offline use, localization, and production hardening

Creates locale, offline package, offline change, accessibility audit, security policy, backup plan/run, recovery test, deployment environment, and release-readiness tables. Existing schema 10 databases migrate in place without recalculating canonical contracts or changing v1.3.0–v1.9.0 repository records.
