# Workspace Export and Restore Bundles

A workspace bundle is a portable JSON package for backup, transfer, and disaster recovery.

## Bundle contents

- workspace projection;
- all canonical contracts in the workspace;
- repository revision and content-hash metadata;
- portfolios and initiative memberships;
- audit records available at export time;
- bundle and database-schema versions.

The bundle schema is `schemas/global_impact_workspace_bundle.schema.json`.

## Restore behavior

Restore imports every contract through the same idempotent import path used by the application service. A bundle hash produces a stable restore receipt. Repeating the same restore returns `unchanged` and does not create duplicate contracts or portfolio memberships.

## Database backup

Workspace bundles are application-level portable exports. `SQLiteImpactRepository.backup_database()` creates a transactionally consistent SQLite backup for infrastructure recovery. Both mechanisms are tested.

## v1.3.0 evidence repository

Workspace bundles now require `evidence_repository`, containing source records, source versions, evidence items, datasets, provenance edges, and claim-evidence links. Restore is idempotent and preserves stable identifiers and checksums.
