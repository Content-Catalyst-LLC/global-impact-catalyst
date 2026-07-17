# WordPress Persistent Workspace

Global Impact Catalyst v1.2.0 preserves the public demonstration shortcode and adds an authenticated workspace.

## Shortcodes

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
```

The demo remains a stateless public contract builder. The workspace requires a signed-in user with `edit_posts` capability.

## Workspace capabilities

- list and search saved initiatives;
- open complete canonical contracts;
- explicit save with revision checks;
- recoverable autosave;
- duplicate initiatives;
- archive and restore;
- import canonical or compact JSON;
- export the current canonical contract.

## WordPress storage

Activation creates prefixed contract, autosave, and audit tables. REST routes live under `global-impact-catalyst/v1`. Requests require WordPress REST nonces and editing capability. The plugin returns HTTP 409 when an expected revision is stale.

The browser continues to use the exact v1.1.0 canonical calculation and validation engine. v1.2.0 adds persistence around that engine rather than changing its mathematical output.

## Evidence ledger

Use `[global_impact_catalyst_evidence_ledger]` for the authenticated v1.3.0 source and evidence interface. It shares the same REST namespace and capability boundary as the persistent workspace.
