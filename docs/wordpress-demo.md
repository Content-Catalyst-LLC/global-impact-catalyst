# WordPress Interfaces

Plugin folder: `wordpress/global-impact-catalyst-demo/`

## Public contract builder

```text
[global_impact_catalyst_demo]
```

The client-side interface creates canonical v1.1.0 contracts without submitting visitor inputs to Sustainable Catalyst. It exposes context, outcome, indicator definition, measurement, source, method, design, review, and claim fields. The output presents contract identity, derived metrics, claim eligibility, validation issues, and downloadable JSON. Multiple shortcode instances are supported through per-instance field IDs.

## Authenticated repository interfaces

```text
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
```

These interfaces require an authenticated user with `edit_posts` capability. They use the `global-impact-catalyst/v1` REST namespace, WordPress REST nonces, capability checks, sanitization, and repository integrity rules.

The v1.6.0 review workflow supports roles, assignments, threaded comments, quality assessments, approval decisions, immutable revisions, corrections, publication approval, and withdrawal records. Publication controls govern release state; they do not certify impact, assurance, regulatory compliance, or causal truth.
