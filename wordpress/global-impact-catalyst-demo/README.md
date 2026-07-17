# Global Impact Catalyst WordPress Plugin

Version 1.5.0 provides five shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
```

The demo is a stateless public canonical-contract builder. The other interfaces require an authenticated user with `edit_posts` capability.

The measurement portfolio adds multi-period observations, aggregate beneficiary definitions and counts, financial records, outcome-portfolio membership, guarded aggregation, JSON export, and privacy-boundary enforcement. It complements the persistent workspace, evidence ledger, and indicator registry.

Activation or plugin-version upgrade creates prefixed contract, audit, evidence, registry, observation, beneficiary, financial, result, relationship, portfolio, membership, and aggregation-run tables. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, sanitization, and repository integrity rules.

The package and plugin are v1.5.0. The embedded canonical contract engine remains v1.1.0, evidence formats remain v1.3.0, and the indicator registry remains v1.4.0 to preserve compatibility.
