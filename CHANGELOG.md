# Changelog

## 1.10.0 — Accessibility, Offline Use, Localization, and Production Hardening

- Added SQLite migration 11 and the v1.10.0 production repository.
- Added English, Spanish, French, custom locale, fallback, and RTL metadata support.
- Added localized SHA-256-bound offline packages and revision-controlled offline change queues.
- Added severity-aware WCAG 2.2, EN 301 549, and Section 508 audit records.
- Added workspace security policies, backup plans, verified SQLite backups, and recovery-test evidence.
- Added deployment-environment records and required release-readiness matrices.
- Added production and workspace schemas, examples, CLI commands, documentation, tests, WordPress routes, and Production Readiness shortcode.
- Preserved canonical contract v1.1.0 and all v1.3.0–v1.9.0 repository semantics.

## 1.9.0 — Public API, Embeds, and Sustainable Catalyst Handoffs

- Added SQLite migration 10 and the v1.9.0 integration repository.
- Added scoped API clients, one-time plaintext key issuance, SHA-256 key storage, revocation, rate limiting, idempotency records, and access auditing.
- Added privacy-safe public initiative and publication APIs restricted to approved, current publication snapshots.
- Added paginated workspace API resources and JSON-LD interoperability metadata.
- Added governed initiative-card, indicator-trend, methodology-panel, portfolio-summary, and report-view embeds.
- Added checksum-bound handoffs to Catalyst Data, Catalyst Analytics R, Site Intelligence, Workbench, Research Lab, Knowledge Library, Research Librarian, Decision Studio, Platform Core, and Advisory.
- Added delivery receipts, integration events, schemas, examples, CLI commands, documentation, tests, WordPress routes, Integration Hub, and public shortcodes.
- Preserved canonical contract v1.1.0 and all v1.3.0–v1.8.0 repository semantics.

## 1.8.0 — Reporting, Publication, and Reproducible Export Studio

- Added SQLite migration 9 and the v1.8.0 reporting repository.
- Added governed report templates, structured report documents, Harvard/APA/plain citations, methodology appendices, accessible HTML, and Markdown exports.
- Added dashboard definitions and cards with text alternatives.
- Added publication snapshots bound to exact contract, evidence, registry, measurement, review, analysis, and report hashes.
- Added deterministic ZIP exports, manifests, SHA-256 checksum files, artifact storage, and independent verification.
- Added reporting schemas, examples, CLI commands, WordPress Reporting Studio, documentation, tests, and release gates.
- Preserved canonical contract v1.1.0 and all v1.3.0–v1.7.0 repository semantics.

## 1.7.0 — Trends, Comparisons, Scenarios, and Uncertainty

- Added SQLite migration 8 and the v1.7.0 analysis repository.
- Added governed trends, benchmarks, comparison sets, scenarios, uncertainty intervals, target gaps, sensitivity analysis, and persisted run hashes.
- Added analysis schemas, examples, CLI commands, WordPress Analysis Studio, documentation, tests, and release gates.
- Preserved canonical contract v1.1.0 and review workflow v1.6.0.


## 1.6.0 — Review, Quality, and Revision Workflow

- Added governed reviewer roles, assignments, comments, quality assessments, approval decisions, corrections, publication controls, withdrawal, and immutable revision history.
- Added SQLite migration 7, review workflow schema/export/restore, service and CLI operations, and an authenticated WordPress review interface.
- Preserved canonical contract v1.1.0, evidence v1.3.0, registry v1.4.0, and measurement v1.5.0 semantics.

All notable changes to Global Impact Catalyst are documented in this file.

## [1.5.0] - 2026-07-17

### Added

- Multi-period observations with complete, missing, late, revised, and partial data states.
- Aggregate disaggregation dimensions, denominator definitions, source and method references, and revision lineage.
- Aggregate-only beneficiary definitions and observations for direct, indirect, and combined reach.
- Counting methods, overlap policies, overlap estimates, and privacy-safe reach summaries.
- Budget, expenditure, commitment, and funding records with funding sources, cost categories, reporting currencies, and explicit exchange rates.
- Cost-per-output, cost-per-outcome, and cost-per-beneficiary calculations with disclosed numerator and denominator records.
- Output, outcome, and long-term-impact records with typed relationships.
- External-factor records and contribution notes with evidence references and limitations.
- Guarded outcome portfolios with unit, period, missing-data, and population-overlap policies.
- v1.5.0 measurement-repository, beneficiary-summary, outcome-portfolio-aggregation, and workspace-bundle JSON Schemas and examples.
- SQLite migration 6, Python service and CLI operations, and authenticated WordPress measurement interface.
- Workspace export and lossless restore of observations, beneficiaries, finances, result relationships, contribution context, portfolios, memberships, and aggregation runs.

### Compatibility

- The canonical contract and exact browser/Python calculation fixtures remain v1.1.0.
- Evidence formats remain v1.3.0 and the indicator registry remains v1.4.0.
- The package, application, database schema, measurement repository, workspace bundle, and WordPress plugin are v1.5.0.
- Existing v1.4.0 databases migrate in place. Existing shortcodes remain available; `[global_impact_catalyst_measurement_portfolio]` is additive.

## [1.4.0] - 2026-07-17

### Added

- Governed registry for standard and workspace-specific units with dimension, canonical conversion, precision, lifecycle, revision, and metadata.
- Eighteen seeded units covering ratios, percentages, counts, currency, energy, mass, greenhouse gases, distance, area, volume, and time.
- Dimension-aware unit conversion with explicit incompatibility errors.
- Versioned indicator definitions with units, direction, formulas, disaggregation dimensions, quality profiles, lifecycle, and immutable content hashes.
- Safe `gic-expression-1.0` arithmetic formula validation and evaluation without arbitrary code execution.
- Point, average, rolling, benchmark, and modelled baseline records and computation.
- Absolute, range, relative, linear, step, exponential, and custom target records and trajectory evaluation.
- Reusable method definitions with input requirements, quality profiles, limitations, lifecycle, and immutable versions.
- Stable bindings from initiative indicators to exact indicator, baseline, target, method, and unit versions.
- Automatic registry materialization when canonical contracts are saved or imported.
- v1.4.0 indicator-registry and workspace-bundle JSON Schemas and examples.
- Registry export and idempotent lossless workspace restore.
- Python service methods, repository CLI commands, authenticated WordPress registry tables, REST routes, responsive interface, and additive shortcode.
- Fifth repeatable SQLite migration and expanded release, schema, formula, conversion, model, WordPress, and recovery tests.

### Compatibility

- The canonical contract, input schema, validation schema, Python engine, browser engine, and fifteen cross-runtime fixtures remain v1.1.0.
- The evidence chain and evidence repository remain v1.3.0.
- The package, application, database schema, indicator registry, workspace bundle, WordPress plugin, and registry interface are v1.4.0.
- Existing v1.3.0 databases migrate in place. Existing demo, workspace, and evidence-ledger shortcodes remain available; `[global_impact_catalyst_indicator_registry]` is additive.

## [1.3.0] - 2026-07-17

### Added

- Structured source registry with title, type, locator, URL, DOI, license, access-rights, lifecycle, and revision metadata.
- Immutable source-version ledger with SHA-256 checksums, MIME type, byte size, capture actor, and capture timestamp.
- Evidence capture for excerpts, quotations, paraphrases, notes, tables, figures, and dataset excerpts.
- Dataset registry with version, license, checksum, schema fingerprint, spatial and temporal coverage, row count, and column count.
- Directed provenance graph connecting sources and methods to baselines, observations, targets, and claims.
- Explicit claim-evidence links for supporting, contradicting, qualifying, and contextual evidence.
- Integrity summaries that report missing source versions, orphan claim links, and contradiction counts without suppressing adverse evidence.
- v1.3.0 evidence-chain, evidence-repository, and workspace-bundle JSON Schemas and examples.
- Workspace export and restore of sources, versions, evidence, datasets, provenance edges, and claim links.
- Repository CLI commands for source registration, file version capture, evidence capture, dataset registration, claim linking, and evidence-chain export.
- Authenticated WordPress evidence ledger, evidence REST routes, database tables, responsive UI, and additive shortcode.
- Fourth repeatable SQLite migration and expanded release, schema, migration, integrity, WordPress, and recovery tests.

### Compatibility

- The canonical contract, input schema, validation schema, Python engine, browser engine, and fifteen cross-runtime fixtures remain v1.1.0.
- The package, application, repository schema, evidence repository, workspace bundle, WordPress plugin, and evidence ledger are v1.3.0.
- Existing v1.2.0 databases migrate in place; existing contracts automatically materialize source versions and provenance when saved or imported.
- Existing `[global_impact_catalyst_demo]` and `[global_impact_catalyst_workspace]` shortcodes remain available. `[global_impact_catalyst_evidence_ledger]` is additive.

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
