# Reporting, Publication, and Reproducible Export Studio

Global Impact Catalyst v1.8.0 converts governed repository state into accessible reports, dashboards, publication snapshots, and reproducible export bundles. The reporting layer references the canonical contract, evidence repository, indicator registry, measurement repository, review workflow, and analysis repository rather than copying ungoverned values into a separate reporting database.

## Governed report documents

A report binds to one workspace and initiative. Each saved document records the source-repository hash, report content hash, template, audience, language, reporting period, structured document, Markdown rendering, accessible HTML rendering, citations, methodology appendix, revision, and generating actor.

Report templates define report type, ordered sections, citation style, and an accessibility profile. Supported report types are impact reports, public briefs, methodology reports, portfolio reports, and board reports. The initial citation styles are Harvard, APA, and a plain structured style.

## Publication snapshots

A publication snapshot can only be created from a publication that has passed the v1.6.0 publication gates and is in the published state. The snapshot records exact SHA-256 hashes for the contract, evidence repository, indicator registry, measurement repository, review workflow, analysis repository, and optional report. This makes later verification explicit even when the live workspace continues to change.

## Dashboards

Dashboards are governed definitions, not screenshots. Each dashboard contains ordered cards with a type, title, subject reference, configuration, and required text alternative. Supported card types include metrics, trends, targets, evidence, quality, budgets, scenarios, and narrative context. Rendering preserves the source record and its boundary language.

## Reproducible exports

The export builder creates a deterministic ZIP with fixed archive timestamps, sorted paths, a machine-readable manifest, SHA-256 checksums, the workspace bundle, and optional report and publication-snapshot artifacts. Rebuilding the same governed state produces identical ZIP bytes.

## Boundaries

Report generation improves traceability and publication discipline. It does not turn observations into assurance, certification, regulatory compliance, audit findings, causal proof, or verified forecasts.
