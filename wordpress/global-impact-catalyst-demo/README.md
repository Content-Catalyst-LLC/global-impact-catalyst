# Global Impact Catalyst WordPress Plugin

Version 1.10.0 provides thirteen shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
[global_impact_catalyst_analysis_studio]
[global_impact_catalyst_reporting_studio]
[global_impact_catalyst_integration_hub]
[global_impact_catalyst_public_profile publication_id="..."]
[global_impact_catalyst_indicator_view publication_id="..."]
[global_impact_catalyst_report_view publication_id="..."]
[global_impact_catalyst_compact_embed slug="..."]
```

The canonical demo is stateless. Repository studios and the Integration Hub require an authenticated user with `edit_posts`. Public shortcodes are read-only and render only published records bound to approved, current publication snapshots.

## Integration Hub

`[global_impact_catalyst_integration_hub]` supports scoped API-client creation, approved public embeds, checksum-bound handoffs to ten Sustainable Catalyst destinations, and integration-repository integrity inspection. API keys are shown once and persisted only as hashes.

## Release identities

```text
Plugin and package:      1.10.0
Database schema:         10
Workspace bundle:        1.10.0
Integration repository:  1.10.0
Public API:               v1
Reporting repository:    1.8.0
Analysis repository:     1.7.0
Review workflow:         1.6.0
Measurement repository:  1.5.0
Indicator registry:      1.4.0
Evidence repository:     1.3.0
Canonical contract:      1.1.0
```

Activation or version upgrade creates prefixed tables for all prior repositories plus API clients, hashed keys, access logs, embeds, platform handoffs, and integration events. REST routes use the `global-impact-catalyst/v1` namespace, WordPress REST nonces, capability checks, sanitization, publication gates, and integrity checks.

API availability and checksum integrity do not constitute assurance, certification, audit, factual verification, regulatory compliance, or causal proof.


## Production readiness shortcode

`[global_impact_catalyst_production_readiness]` provides the authenticated v1.10.0 interface for localization, offline packages, accessibility evidence, security policy, deployment environments, and release readiness.
