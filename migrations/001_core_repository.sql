CREATE TABLE IF NOT EXISTS repository_entities (
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    workspace_id TEXT,
    initiative_id TEXT,
    parent_id TEXT,
    name TEXT NOT NULL DEFAULT '',
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    archived_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    document_json TEXT NOT NULL,
    PRIMARY KEY (entity_type, entity_id)
);
CREATE INDEX IF NOT EXISTS idx_entities_workspace ON repository_entities(workspace_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_initiative ON repository_entities(initiative_id, entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_name ON repository_entities(entity_type, name);
CREATE TABLE IF NOT EXISTS canonical_contracts (
    record_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL UNIQUE,
    contract_version TEXT NOT NULL,
    save_state TEXT NOT NULL DEFAULT 'saved',
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1,
    content_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    contract_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_contracts_workspace ON canonical_contracts(workspace_id, updated_at);
