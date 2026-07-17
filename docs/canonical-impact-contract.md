# Canonical Impact Contract — v1.1.0

The canonical impact contract is the durable exchange object produced by both runtime implementations.

## Root metadata

| Field | Meaning |
|---|---|
| `contract_type` | Constant `global_impact_contract` |
| `contract_version` | Behavioral contract version |
| `schema_version` | JSON Schema version governing the object |
| `record_id` | Stable deterministic contract identifier |
| `created_at` / `updated_at` | RFC 3339 timestamps |
| `lifecycle_status` | Draft, needs review, reviewed, or published |
| `provenance` | Generator, input fingerprint, and migration metadata |

## Facts

`facts` contains entered or migrated assertions. It includes the workspace and initiative context, intended goal and outcome, versioned indicator definition, baseline, target, observations, source records, methods, population groups, geographies, and budgets.

Facts do not contain calculated progress or generated interpretation language.

## Derived

`derived.metrics` contains reproducible calculations and a `calculation_method` object naming the engine version, rounding rule, and progress formula.

`derived.interpretations` contains generated explanatory text with evidence references.

`derived.claims` contains the claim type, exact statement, confidence, evidence references, design metadata, and an eligibility result with blocking validation issue IDs.

## Governance

`governance.reviews` records current review state and confidence. `revisions` begins with the canonical-contract creation event. `publications` is empty until the contract is published.

## Validation

`validation.valid` is false whenever at least one error exists. Warning-only contracts remain valid. Validation does not establish truth, evidence quality, source authenticity, or legal sufficiency.

## Identity

IDs use the form `gic-<entity>-<16 hex characters>`. They are deterministically generated from normalized input and the contract record ID. Rebuilding the same input yields the same IDs, enabling reproducible fixtures and stable references without a database.
