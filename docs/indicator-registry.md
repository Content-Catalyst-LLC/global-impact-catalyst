# Indicator Registry

Global Impact Catalyst v1.4.0 adds a governed registry for reusable measurement definitions. The registry is separate from the canonical contract: a contract records what a specific initiative asserted at a specific time, while the registry records the controlled definitions and versions that make indicators reusable across initiatives and portfolios.

## Registry objects

- **Unit definition** — code, symbol, dimension, canonical conversion rule, precision, lifecycle, and revision.
- **Indicator definition** — name, description, direction, unit, formula, disaggregation dimensions, quality profile, lifecycle, and immutable versions.
- **Baseline model** — model type, unit, reference period, parameters, formula, quality profile, and immutable versions.
- **Target model** — target type, unit, target value or range, trajectory, milestones, formula, and immutable versions.
- **Method definition** — method name, design, input requirements, quality profile, limitations, lifecycle, and immutable versions.
- **Registry binding** — stable link from an initiative indicator to the exact indicator, baseline, target, and method versions used by that initiative.

## Versioning

Mutable registry records hold current lifecycle and revision metadata. Their version tables hold immutable JSON documents and content hashes. Registering a changed definition creates a new version. Existing bindings continue to point to the version that was current when the binding was created or refreshed.

## Automatic materialization

When a canonical contract is saved or imported, the repository:

1. resolves or creates the indicator unit;
2. resolves or creates an indicator definition;
3. materializes baseline and target models from entered facts;
4. materializes a method definition when method facts are present;
5. writes a stable registry binding for the initiative indicator.

This process is additive. It does not alter the canonical v1.1.0 contract or recalculate its metrics.

## Export and restore

`export_indicator_registry(workspace_id)` returns a v1.4.0 registry containing units, definitions, immutable versions, models, methods, bindings, and integrity counts. The workspace bundle embeds this registry and restores it idempotently with stable identifiers.

## Integrity checks

The registry reports:

- missing unit references;
- orphan bindings;
- counts for definitions and immutable versions;
- the number of active bindings.

Integrity checks establish internal referential consistency. They do not certify that an indicator is valid for a particular policy, population, geography, or causal question.
