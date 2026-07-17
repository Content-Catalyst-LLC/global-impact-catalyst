CREATE TABLE IF NOT EXISTS import_records (
    import_id TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL UNIQUE,
    source_contract_version TEXT NOT NULL,
    record_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    status TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    workspace_id TEXT,
    initiative_id TEXT,
    revision INTEGER,
    details_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_workspace ON audit_log(workspace_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id, occurred_at);
CREATE TABLE IF NOT EXISTS restore_records (
    restore_id TEXT PRIMARY KEY,
    bundle_hash TEXT NOT NULL UNIQUE,
    restored_at TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    summary_json TEXT NOT NULL
);
