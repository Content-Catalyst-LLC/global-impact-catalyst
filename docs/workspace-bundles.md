# Workspace Export and Restore Bundles

A workspace bundle is a portable JSON package for backup, transfer, and disaster recovery.

## Bundle contents

- workspace projection and canonical contracts;
- repository revisions, portfolios, memberships, and audit records;
- complete evidence repository;
- complete indicator registry;
- complete v1.5.0 measurement repository;
- bundle and database-schema versions.

The bundle schema is `schemas/global_impact_workspace_bundle.schema.json`.

## Restore behavior

Restore imports canonical contracts through the idempotent import path and restores evidence, registry, and measurement records with stable identifiers. A bundle hash produces a stable restore receipt. Repeating the same restore returns `unchanged` and does not duplicate records, versions, memberships, or aggregation runs.

## Database backup

Workspace bundles are application-level portable exports. `SQLiteImpactRepository.backup_database()` creates a transactionally consistent SQLite backup for infrastructure recovery. Both mechanisms are tested.

## Compatibility layers

The evidence section remains v1.3.0. The indicator-registry section remains v1.4.0. The required measurement-repository and workspace-bundle sections are v1.5.0 and require database schema 6.
