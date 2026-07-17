# Governed Embeds

v1.9.0 supports five read-only embed types: `initiative_card`, `indicator_trend`, `methodology_panel`, `portfolio_summary`, and `report_view`.

An embed must be bound to a published record and an approved publication snapshot. Its definition records the workspace, publication, snapshot, type, title, public slug, configuration, lifecycle status, revision, and content hash. Rendering rechecks publication state and snapshot identity before returning accessible HTML.

Embeds contain no edit controls and do not expose source contents, evidence excerpts, reviewer notes, credentials, or workspace internals. Each render includes an accessible label and the public limitations boundary. Disabling or withdrawing the governing record prevents public rendering.

WordPress provides `[global_impact_catalyst_compact_embed slug="..."]` plus dedicated approved profile, indicator, and report shortcodes.
