# Global Impact Catalyst WordPress Plugin

Version 1.7.0 provides six shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
```

The demo is a stateless public canonical-contract builder. The other interfaces require an authenticated user with `edit_posts` capability.

The review workflow adds governed roles, scoped assignments, threaded comments, weighted quality assessments, approval decisions, immutable contract revisions, correction records, publication approval, and withdrawal history. It complements the persistent workspace, evidence ledger, indicator registry, and measurement portfolio.

Activation or plugin-version upgrade creates prefixed contract, audit, evidence, registry, observation, beneficiary, financial, result, relationship, portfolio, review, correction, publication, and publication-event tables. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, sanitization, and repository integrity rules.

The package and plugin are v1.6.0. The embedded canonical contract engine remains v1.1.0, evidence formats remain v1.3.0, the indicator registry remains v1.4.0, and the measurement layer remains v1.5.0 to preserve compatibility.

## Analysis Studio

Use `[global_impact_catalyst_analysis_studio]` for authenticated benchmarks, trends, comparison sets, scenarios, uncertainty, and sensitivity records.
