# Changelog

All notable changes to Global Impact Catalyst are documented in this file.

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
