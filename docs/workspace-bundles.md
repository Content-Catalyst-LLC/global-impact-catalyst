# Workspace Export and Restore Bundles

A v2.0.0 workspace bundle is a portable JSON package for backup, transfer, institutional handoff, federation, and disaster recovery.

## Bundle contents

- workspace projection and canonical contracts;
- repository revisions, portfolios, memberships, imports, and audit records;
- evidence repository v1.3.0;
- indicator registry v1.4.0;
- measurement repository v1.5.0;
- review workflow v1.6.0;
- analysis repository v1.7.0;
- reporting repository v1.8.0;
- integration repository v1.9.0;
- production repository v1.10.0;
- connected platform repository v2.0.0, including institutions, members, workspace links, connections, decision pathways, workflows, workflow runs, unified snapshots, and platform events;
- bundle version 2.0.0 and database schema version 12.

The bundle schema is `schemas/global_impact_workspace_bundle.schema.json`.

## Restore behavior

Restore imports canonical contracts through the idempotent import path and then restores each governed repository layer in dependency order. The connected platform layer is restored last so institution-workspace relationships and cross-repository snapshots refer to records that already exist. Stable identifiers, revisions, timestamps, hashes, publication links, workflow histories, and event correlations are preserved.

A bundle hash produces a stable restore receipt. Repeating the same restore returns `unchanged` and does not duplicate records.

## Connected platform restore

The v2.0.0 `platform_repository` preserves:

- institution and membership identities without plaintext credential material;
- role and permission assignments;
- institution-to-workspace relationships and policies;
- platform connection contracts and verification results;
- decision-pathway nodes and edges;
- workflow definitions and deterministic execution results;
- source repository hashes and platform snapshot hashes; and
- event payload hashes and correlation identifiers.

Restore does not execute workflows, contact connected services, rotate keys, or treat historical verification as a live health check.

## Reproducible exports

A workspace bundle is a complete application-level backup. A reproducible export is a publication-oriented deterministic ZIP containing a normalized workspace bundle and optional report and publication snapshot. It includes `manifest.json` and `SHA256SUMS.txt`.

## Database backup

`SQLiteImpactRepository.backup_database()` creates a transactionally consistent SQLite backup for infrastructure recovery. Workspace bundles and SQLite backups serve different recovery needs; both are tested.
