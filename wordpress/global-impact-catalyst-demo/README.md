# Global Impact Catalyst WordPress Plugin

Version 1.8.0 provides eight shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
[global_impact_catalyst_analysis_studio]
[global_impact_catalyst_reporting_studio]
```

The public demo is a stateless canonical-contract builder. The seven repository studios require an authenticated user with `edit_posts` capability.

## Reporting Studio

`[global_impact_catalyst_reporting_studio]` supports:

- report-template creation;
- accessible HTML and Markdown reports;
- methodology metadata and limitations;
- dashboard definitions;
- publication snapshots linked to published review records;
- stored reproducible artifact sets;
- manifests and SHA-256 checksums;
- reporting-repository integrity inspection.

The Python repository and CLI additionally create deterministic ZIP archives with fixed timestamps and independently verifiable artifact checksums.

## Release identities

```text
Plugin and package:     1.8.0
Database schema:        9
Reporting repository:   1.8.0
Analysis repository:    1.7.0
Review workflow:        1.6.0
Measurement repository: 1.5.0
Indicator registry:     1.4.0
Evidence repository:    1.3.0
Canonical contract:     1.1.0
```

Activation or version upgrade creates prefixed tables for contracts, evidence, registry definitions, observations, beneficiaries, finances, outcome portfolios, review workflows, analysis records, reports, dashboards, snapshots, bundles, and artifacts. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, sanitization, and repository integrity rules.

Publication and checksum integrity do not constitute assurance, certification, audit, source authentication, causal proof, or a verified forecast.
