# Export Specification — v1.1.0

Global Impact Catalyst exports UTF-8 JSON governed by `schemas/global_impact_contract.schema.json` and optional Markdown generated from the same in-memory contract.

## JSON guarantees

- Contract type and versions are explicit.
- Stable IDs and timestamps are attached to material entities.
- Omitted optional numbers remain `null` or absent entity arrays; explicit zero remains zero.
- Entered facts and derived values are separated.
- Calculation provenance is included with derived metrics.
- Validation and claim eligibility remain attached to invalid drafts.
- Boundaries and traceability path remain attached to every export.

## Reproducibility

Use `--generated-at` for deterministic timestamps. Normalized input also produces deterministic record, entity, fingerprint, and issue IDs.

## Markdown

The Markdown brief summarizes contract identity, entered facts, derived metrics, claim eligibility, validation, interpretations, and boundaries. JSON remains the canonical machine-readable form.
