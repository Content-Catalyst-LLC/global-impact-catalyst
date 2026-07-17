# WordPress Persistent Workspace

Global Impact Catalyst preserves the public demonstration shortcode and provides authenticated repository interfaces.

## Shortcodes

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
```

The demo remains a stateless public contract builder. The other interfaces require a signed-in user with `edit_posts` capability.

## Workspace capabilities

- list and search saved initiatives;
- open complete canonical contracts;
- explicit save with revision checks;
- recoverable autosave;
- duplicate initiatives;
- archive and restore;
- import canonical or compact JSON;
- export the current canonical contract.

## Evidence ledger

The evidence ledger registers sources, preserves SHA-256 source versions, captures evidence and dataset metadata, links evidence to claims, displays contradictions, and exports an initiative evidence chain.

## Indicator registry

The v1.4.0 registry interface:

- lists seeded and workspace units;
- registers custom units;
- creates versioned indicator definitions;
- creates baseline and target models;
- creates reusable method definitions;
- displays contract-materialized registry bindings;
- exports the complete workspace registry.

## WordPress storage and REST

Activation creates prefixed contract, autosave, audit, evidence, unit, indicator, baseline, target, method, version, and binding tables. REST routes live under `global-impact-catalyst/v1`. Requests require WordPress REST nonces and editing capability. Input is sanitized and stale revisions are rejected.

The browser continues to use the exact v1.1.0 canonical calculation and validation engine. Repository, evidence, and registry releases add durable governance around that engine rather than changing its mathematical output.


## v1.5.0 measurement interface

`[global_impact_catalyst_measurement_portfolio]` adds authenticated observation, aggregate beneficiary, financial-record, outcome-portfolio, and guarded aggregation workflows. These records are included in v1.5.0 workspace bundles and remain separate from the public canonical-contract demo.
