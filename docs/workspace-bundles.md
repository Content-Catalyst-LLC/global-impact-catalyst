# Workspace Export and Restore Bundles

A workspace bundle is a portable JSON package for backup, transfer, and disaster recovery.

## Bundle contents

- workspace projection;
- all canonical contracts in the workspace;
- repository revision and content-hash metadata;
- portfolios and initiative memberships;
- audit records available at export time;
- complete evidence repository;
- complete indicator registry;
- bundle and database-schema versions.

The bundle schema is `schemas/global_impact_workspace_bundle.schema.json`.

## Restore behavior

Restore imports every contract through the same idempotent import path used by the application service. A bundle hash produces a stable restore receipt. Repeating the same restore returns `unchanged` and does not create duplicate contracts, portfolio memberships, sources, evidence links, registry versions, or bindings.

## Database backup

Workspace bundles are application-level portable exports. `SQLiteImpactRepository.backup_database()` creates a transactionally consistent SQLite backup for infrastructure recovery. Both mechanisms are tested.

## Evidence repository

The required `evidence_repository` section contains source records, source versions, evidence items, datasets, provenance edges, and claim-evidence links. Evidence format compatibility remains v1.3.0.

## v1.4.0 indicator registry

The required `indicator_registry` section contains standard and custom units, indicator definitions and immutable versions, baseline models, target models, method definitions, stable bindings, and integrity counts. Restore preserves identifiers, version documents, content hashes, and the exact unit/model references used by each binding.
