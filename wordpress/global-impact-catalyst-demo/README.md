# Global Impact Catalyst WordPress Plugin

Version 1.4.0 provides four shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
```

The demo is a stateless public canonical-contract builder. The workspace, evidence ledger, and indicator registry require an authenticated user with `edit_posts` capability.

The indicator registry adds:

- seeded standard units and workspace-specific unit registration;
- governed indicator definitions and immutable versions;
- baseline and target model registration;
- reusable method definitions;
- automatic materialization and binding from saved contracts;
- workspace registry inspection and JSON export.

The evidence ledger continues to provide structured sources, SHA-256 source versions, evidence capture, dataset metadata, claim-evidence links, and provenance-chain export.

Activation or automatic plugin-version upgrade creates prefixed contract, autosave, audit, evidence, unit, indicator-definition, baseline, target, method, version, and binding tables. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, sanitization, and repository integrity rules.

The package is v1.4.0. The embedded canonical contract engine remains v1.1.0 and the evidence-chain format remains v1.3.0 to preserve exact calculation and evidence compatibility.
