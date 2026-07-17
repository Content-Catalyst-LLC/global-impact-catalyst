CREATE TABLE IF NOT EXISTS report_templates (
    template_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    report_type TEXT NOT NULL DEFAULT 'impact_report',
    sections_json TEXT NOT NULL,
    citation_style TEXT NOT NULL DEFAULT 'harvard',
    accessibility_profile_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_report_templates_name ON report_templates(workspace_id, name);

CREATE TABLE IF NOT EXISTS report_documents (
    report_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    template_id TEXT,
    title TEXT NOT NULL,
    report_type TEXT NOT NULL DEFAULT 'impact_report',
    audience TEXT NOT NULL DEFAULT 'public',
    language TEXT NOT NULL DEFAULT 'en',
    period_label TEXT NOT NULL DEFAULT '',
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    source_bundle_hash TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    document_json TEXT NOT NULL,
    rendered_markdown TEXT NOT NULL,
    rendered_html TEXT NOT NULL,
    citations_json TEXT NOT NULL,
    methodology_json TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (template_id) REFERENCES report_templates(template_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_report_documents_workspace ON report_documents(workspace_id, initiative_id, updated_at);

CREATE TABLE IF NOT EXISTS dashboard_definitions (
    dashboard_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    audience TEXT NOT NULL DEFAULT 'internal',
    layout_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dashboard_definitions_workspace ON dashboard_definitions(workspace_id, initiative_id, name);

CREATE TABLE IF NOT EXISTS dashboard_cards (
    card_id TEXT PRIMARY KEY,
    dashboard_id TEXT NOT NULL,
    card_type TEXT NOT NULL,
    title TEXT NOT NULL,
    subject_type TEXT NOT NULL DEFAULT '',
    subject_id TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL DEFAULT 0,
    alt_text TEXT NOT NULL DEFAULT '',
    configuration_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (dashboard_id) REFERENCES dashboard_definitions(dashboard_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_dashboard_cards_dashboard ON dashboard_cards(dashboard_id, position, title);

CREATE TABLE IF NOT EXISTS publication_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    publication_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    report_id TEXT,
    release_label TEXT NOT NULL DEFAULT '',
    snapshot_hash TEXT NOT NULL,
    contract_hash TEXT NOT NULL,
    evidence_hash TEXT NOT NULL,
    registry_hash TEXT NOT NULL,
    measurement_hash TEXT NOT NULL,
    review_hash TEXT NOT NULL,
    analysis_hash TEXT NOT NULL,
    report_hash TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (publication_id) REFERENCES publication_records(publication_id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES report_documents(report_id) ON DELETE SET NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_publication_snapshot_unique ON publication_snapshots(publication_id, snapshot_hash);

CREATE TABLE IF NOT EXISTS export_bundles (
    export_bundle_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    report_id TEXT,
    publication_snapshot_id TEXT,
    bundle_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'complete',
    manifest_hash TEXT NOT NULL,
    archive_hash TEXT NOT NULL DEFAULT '',
    artifact_count INTEGER NOT NULL DEFAULT 0,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (report_id) REFERENCES report_documents(report_id) ON DELETE SET NULL,
    FOREIGN KEY (publication_snapshot_id) REFERENCES publication_snapshots(snapshot_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_export_bundles_workspace ON export_bundles(workspace_id, created_at);

CREATE TABLE IF NOT EXISTS export_artifacts (
    artifact_id TEXT PRIMARY KEY,
    export_bundle_id TEXT NOT NULL,
    artifact_path TEXT NOT NULL,
    media_type TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    content_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(export_bundle_id, artifact_path),
    FOREIGN KEY (export_bundle_id) REFERENCES export_bundles(export_bundle_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_export_artifacts_bundle ON export_artifacts(export_bundle_id, artifact_path);
