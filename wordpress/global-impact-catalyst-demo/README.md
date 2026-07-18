# Global Impact Catalyst WordPress Plugin

Version 2.0.0 provides fifteen shortcodes.

## Authenticated platform and repository interfaces

```text
[global_impact_catalyst_platform_hub]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
[global_impact_catalyst_analysis_studio]
[global_impact_catalyst_reporting_studio]
[global_impact_catalyst_integration_hub]
[global_impact_catalyst_production_readiness]
```

## Public interfaces

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_public_profile publication_id="..."]
[global_impact_catalyst_indicator_view publication_id="..."]
[global_impact_catalyst_report_view publication_id="..."]
[global_impact_catalyst_compact_embed slug="..."]
```

The canonical demo is stateless. Repository studios, the Integration Hub, Production Readiness, and the Connected Platform Hub require an authenticated user with `edit_posts`. Public publication shortcodes are read-only and render only records bound to approved, current publication snapshots.

## Connected Platform Hub

`[global_impact_catalyst_platform_hub]` provides authenticated institutional workspace coordination. It can create institutions and members, register and verify platform connections, define evidence-to-decision pathways, and create cross-repository platform snapshots. REST operations use the `global-impact-catalyst/v1` namespace with capability checks and WordPress nonces.

## Release identities

```text
Plugin and package:       2.0.0
Database schema:          12
Workspace bundle:         2.0.0
Platform repository:      2.0.0
Production repository:    1.10.0
Integration repository:   1.9.0
Public API:                v1
Reporting repository:     1.8.0
Analysis repository:      1.7.0
Review workflow:          1.6.0
Measurement repository:   1.5.0
Indicator registry:       1.4.0
Evidence repository:      1.3.0
Canonical contract:       1.1.0
```

Activation or version upgrade creates prefixed tables for all prior repositories plus institutions, institutional memberships, workspace links, platform connections, decision pathways, workflows and runs, platform snapshots, and platform events.

Platform connectivity and checksum integrity do not constitute assurance, certification, audit, factual verification, regulatory compliance, institutional endorsement, or causal proof.
