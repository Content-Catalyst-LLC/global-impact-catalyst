CREATE TABLE IF NOT EXISTS source_records (
    source_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'document',
    locator TEXT NOT NULL DEFAULT '',
    creator TEXT NOT NULL DEFAULT '',
    publisher TEXT NOT NULL DEFAULT '',
    published_at TEXT,
    retrieved_at TEXT,
    url TEXT NOT NULL DEFAULT '',
    doi TEXT NOT NULL DEFAULT '',
    license TEXT NOT NULL DEFAULT 'not_recorded',
    access_rights TEXT NOT NULL DEFAULT 'not_recorded',
    lifecycle_status TEXT NOT NULL DEFAULT 'active',
    current_version INTEGER NOT NULL DEFAULT 0,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_source_records_workspace ON source_records(workspace_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_source_records_initiative ON source_records(initiative_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_source_records_title ON source_records(title);

CREATE TABLE IF NOT EXISTS source_versions (
    source_version_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    version_label TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    checksum_algorithm TEXT NOT NULL DEFAULT 'sha256',
    checksum_value TEXT NOT NULL,
    mime_type TEXT NOT NULL DEFAULT 'application/json',
    size_bytes INTEGER,
    captured_at TEXT NOT NULL,
    captured_by TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(source_id, version_number),
    UNIQUE(source_id, checksum_algorithm, checksum_value),
    FOREIGN KEY (source_id) REFERENCES source_records(source_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_source_versions_source ON source_versions(source_id, version_number);

CREATE TABLE IF NOT EXISTS evidence_items (
    evidence_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_version_id TEXT,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    evidence_type TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    locator TEXT NOT NULL DEFAULT '',
    exact_quote TEXT NOT NULL DEFAULT '',
    paraphrase TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    page_start INTEGER,
    page_end INTEGER,
    character_start INTEGER,
    character_end INTEGER,
    captured_at TEXT NOT NULL,
    captured_by TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    archived_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES source_records(source_id) ON DELETE CASCADE,
    FOREIGN KEY (source_version_id) REFERENCES source_versions(source_version_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence_items(source_id, captured_at);
CREATE INDEX IF NOT EXISTS idx_evidence_initiative ON evidence_items(initiative_id, captured_at);

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_version_id TEXT,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    title TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    landing_page TEXT NOT NULL DEFAULT '',
    distribution_url TEXT NOT NULL DEFAULT '',
    license TEXT NOT NULL DEFAULT 'not_recorded',
    checksum_algorithm TEXT NOT NULL DEFAULT 'sha256',
    checksum_value TEXT NOT NULL,
    schema_fingerprint TEXT NOT NULL DEFAULT '',
    temporal_coverage TEXT NOT NULL DEFAULT '',
    spatial_coverage TEXT NOT NULL DEFAULT '',
    row_count INTEGER,
    column_count INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES source_records(source_id) ON DELETE CASCADE,
    FOREIGN KEY (source_version_id) REFERENCES source_versions(source_version_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_datasets_source ON datasets(source_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_datasets_initiative ON datasets(initiative_id, updated_at);

CREATE TABLE IF NOT EXISTS provenance_edges (
    edge_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    process_name TEXT NOT NULL DEFAULT '',
    method_id TEXT,
    method_version TEXT NOT NULL DEFAULT '',
    occurred_at TEXT NOT NULL,
    actor TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(subject_type, subject_id, predicate, object_type, object_id, method_id)
);
CREATE INDEX IF NOT EXISTS idx_provenance_initiative ON provenance_edges(initiative_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_provenance_subject ON provenance_edges(subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_provenance_object ON provenance_edges(object_type, object_id);

CREATE TABLE IF NOT EXISTS claim_evidence_links (
    claim_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    relationship TEXT NOT NULL DEFAULT 'supports',
    strength TEXT NOT NULL DEFAULT 'direct',
    notes TEXT NOT NULL DEFAULT '',
    linked_at TEXT NOT NULL,
    linked_by TEXT NOT NULL,
    PRIMARY KEY (claim_id, evidence_id, relationship),
    FOREIGN KEY (evidence_id) REFERENCES evidence_items(evidence_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_claim_evidence_claim ON claim_evidence_links(claim_id, linked_at);
