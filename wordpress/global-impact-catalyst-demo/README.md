# Global Impact Catalyst WordPress Plugin

Version 1.3.0 provides three shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
```

The demo is a stateless public canonical-contract builder. The workspace and evidence ledger require an authenticated user with `edit_posts` capability.

The evidence ledger adds:

- structured source registration
- SHA-256 source-version records
- evidence quotation, excerpt, paraphrase, and note capture
- dataset integrity metadata
- claim-evidence links for support, contradiction, qualification, and context
- provenance-chain inspection and JSON export

Activation or automatic plugin-version upgrade creates prefixed contract, autosave, audit, source, source-version, evidence, dataset, provenance, and claim-link tables. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, sanitization, and repository integrity rules.

The package is v1.3.0. The embedded canonical contract engine remains v1.1.0 to preserve exact Python/browser calculation parity.
