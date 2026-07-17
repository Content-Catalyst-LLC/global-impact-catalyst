# Changelog

All notable changes to Global Impact Catalyst are documented in this file.

## [1.2.0] - 2026-07-17

### Added

- SQLite repository abstraction with repeatable, version-tracked database migrations.
- Durable canonical contract snapshots and indexed projections for workspaces, initiatives, goals, indicators, observations, targets, and sources.
- Shared application service for create, explicit save, autosave, import, duplicate, list, export, and restore operations.
- Initiative and portfolio search, archive, restore, duplication, and membership workflows.
- Recoverable draft autosaves and optimistic concurrency conflict responses.
- Idempotent v1.0.x and v1.1.0 imports with audit receipts.
- Workspace export/restore bundles and transactionally consistent SQLite backups.
- Persistent authenticated WordPress workspace shortcode and REST repository.
- Repository CLI, workspace bundle schema, persistence documentation, migration tests, and backup/restore tests.

### Compatibility

- The canonical contract, schemas, and cross-runtime calculation engine remain v1.1.0 because persistence does not change the contract shape or mathematical output.
- The package, application, WordPress plugin, repository workflows, and workspace bundle are v1.2.0.
- The public `[global_impact_catalyst_demo]` shortcode remains available; `[global_impact_catalyst_workspace]` is additive.

## [1.1.0] - 2026-07-17

### Added

- Canonical entity-oriented impact contract with stable deterministic identifiers and timestamps.
- Contract, schema, record, lifecycle, and provenance metadata.
- Explicit `facts`, `derived`, `governance`, and `validation` layers.
- Structured validation issues with severity, field path, rule ID, message, and remediation.
- Semantic rules for required facts, period ordering, unit compatibility, indicator direction, baseline/target compatibility, source locators, and method detail.
- Governed descriptive, progress, comparison, contribution, and causal claim types.
- Evidence and design gates for stronger claim language.
- Lossless migration from v1.0.x flat records with the original record retained in provenance.
- Canonical contract, compatibility, authoring-input, and validation-result JSON Schemas.
- Fifteen exact cross-runtime fixtures, expanded core tests, and migration tests.
- Expanded WordPress contract builder with evidence, design, claim, and validation fields.
- Contract reference, validation-rule catalog, claim governance, and migration documentation.

### Changed

- `build_impact_record` now remains as a compatibility alias but returns the canonical v1.1.0 contract.
- JSON downloads now use the canonical contract rather than the v1.0.x flat record.
- Markdown exports now distinguish entered facts, derived metrics, claim eligibility, validation, and boundaries.
- The traceability path now covers governance and publication entities.

### Compatibility

- v1.0.x flat records remain readable through `migrate_legacy_record` and the CLI `--migrate` option.
- The browser still exports `buildImpactRecord` as an alias to `buildImpactContract`.

## [1.0.1] - 2026-07-17

### Fixed

- Corrected `higher_is_better` parsing so string values such as `"false"` no longer become truthy in Python.
- Preserved `null` versus explicit zero semantics for beneficiaries and budget values across Python and browser runtimes.
- Aligned Python and JavaScript rounding, statuses, interpretation notes, traceability paths, boundaries, enum normalization, and optional-value handling.
- Replaced static WordPress form IDs with per-shortcode-instance IDs.
- Corrected repository documentation and test-path drift.

### Added

- Canonical input and fully typed output JSON Schemas for v1.0.1.
- Twelve cross-runtime golden fixtures covering normal and edge-case calculations.
- Python core, schema, browser-parity, malformed-input, WordPress contract, and release-contract tests.
- Data-quality component breakdown and explicit documentation that the score is a completeness/review heuristic rather than evidence assurance.
- Accessible form validation summary, focus handling, required-field checks, and live status announcements.
- Reproducible output timestamps for fixtures and release generation.
- Portable release smoke test and release-contract scripts.

## [1.0.0] - 2026-07-01

### Added

- Initial dependency-light Python impact-record generator.
- Browser-based WordPress demo shortcode.
- JSON and Markdown export support.
- Initial output schema, sample data, examples, documentation, tests, and CI workflow.
