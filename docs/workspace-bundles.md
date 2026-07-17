# Workspace Export and Restore Bundles

A v1.8.0 workspace bundle is a portable JSON package for backup, transfer, institutional handoff, and disaster recovery.

## Bundle contents

- workspace projection and canonical contracts;
- repository revisions, portfolios, memberships, imports, and audit records;
- evidence repository v1.3.0;
- indicator registry v1.4.0;
- measurement repository v1.5.0;
- review workflow v1.6.0;
- analysis repository v1.7.0;
- reporting repository v1.8.0;
- report templates, documents, dashboards, snapshots, export bundles, manifests, checksums, and artifact content;
- bundle version 1.8.0 and database schema version 9.

The bundle schema is `schemas/global_impact_workspace_bundle.schema.json`.

## Restore behavior

Restore imports canonical contracts through the idempotent import path and then restores each governed repository layer in dependency order. Stable identifiers, revisions, timestamps, hashes, publication links, dashboard cards, and export artifacts are preserved. A bundle hash produces a stable restore receipt. Repeating the same restore returns `unchanged` and does not duplicate records.

Reporting restore verifies report document hashes, snapshot hashes, artifact byte sizes, artifact checksums, bundle artifact counts, manifest hashes, and deterministically rebuilt archive hashes.

## Reproducible exports

A workspace bundle is a complete application-level backup. A reproducible export is a publication-oriented deterministic ZIP containing a normalized workspace bundle and optional report and publication snapshot. It includes `manifest.json` and `SHA256SUMS.txt`.

## Database backup

`SQLiteImpactRepository.backup_database()` creates a transactionally consistent SQLite backup for infrastructure recovery. Workspace bundles and SQLite backups serve different recovery needs; both are tested.
