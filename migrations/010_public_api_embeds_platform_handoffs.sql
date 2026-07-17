PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS api_clients (
    client_id TEXT PRIMARY KEY,
    workspace_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    client_type TEXT NOT NULL DEFAULT 'service',
    lifecycle_status TEXT NOT NULL DEFAULT 'active',
    rate_limit_per_minute INTEGER NOT NULL DEFAULT 60,
    revision INTEGER NOT NULL DEFAULT 1,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_api_clients_workspace ON api_clients(workspace_id, lifecycle_status, name);

CREATE TABLE IF NOT EXISTS api_keys (
    api_key_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    key_prefix TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    scopes_json TEXT NOT NULL,
    expires_at TEXT,
    revoked_at TEXT,
    last_used_at TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES api_clients(client_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_api_keys_client ON api_keys(client_id, revoked_at, expires_at);

CREATE TABLE IF NOT EXISTS api_idempotency_records (
    idempotency_id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    operation TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    response_hash TEXT NOT NULL,
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    UNIQUE(client_id, idempotency_key, operation),
    FOREIGN KEY (client_id) REFERENCES api_clients(client_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS api_rate_windows (
    client_id TEXT NOT NULL,
    window_start TEXT NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (client_id, window_start),
    FOREIGN KEY (client_id) REFERENCES api_clients(client_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS api_access_log (
    access_id TEXT PRIMARY KEY,
    client_id TEXT,
    api_key_id TEXT,
    workspace_id TEXT,
    operation TEXT NOT NULL,
    resource_type TEXT NOT NULL DEFAULT '',
    resource_id TEXT NOT NULL DEFAULT '',
    scope TEXT NOT NULL DEFAULT '',
    status_code INTEGER NOT NULL,
    occurred_at TEXT NOT NULL,
    request_hash TEXT NOT NULL DEFAULT '',
    response_hash TEXT NOT NULL DEFAULT '',
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES api_clients(client_id) ON DELETE SET NULL,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(api_key_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_api_access_workspace ON api_access_log(workspace_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_api_access_client ON api_access_log(client_id, occurred_at);

CREATE TABLE IF NOT EXISTS embed_definitions (
    embed_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    publication_id TEXT,
    publication_snapshot_id TEXT,
    embed_type TEXT NOT NULL,
    title TEXT NOT NULL,
    public_slug TEXT NOT NULL UNIQUE,
    configuration_json TEXT NOT NULL,
    accessibility_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'active',
    revision INTEGER NOT NULL DEFAULT 1,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (publication_id) REFERENCES publication_records(publication_id) ON DELETE SET NULL,
    FOREIGN KEY (publication_snapshot_id) REFERENCES publication_snapshots(snapshot_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_embeds_workspace ON embed_definitions(workspace_id, lifecycle_status, embed_type);

CREATE TABLE IF NOT EXISTS platform_handoffs (
    handoff_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    destination TEXT NOT NULL,
    handoff_type TEXT NOT NULL,
    handoff_version TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ready',
    source_snapshot_hash TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    idempotency_key TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT,
    delivery_receipt_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(workspace_id, destination, idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_handoffs_workspace ON platform_handoffs(workspace_id, destination, created_at);
CREATE INDEX IF NOT EXISTS idx_handoffs_initiative ON platform_handoffs(initiative_id, destination, created_at);

CREATE TABLE IF NOT EXISTS integration_events (
    event_id TEXT PRIMARY KEY,
    workspace_id TEXT,
    initiative_id TEXT,
    event_type TEXT NOT NULL,
    event_version TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_integration_events_workspace ON integration_events(workspace_id, created_at);
