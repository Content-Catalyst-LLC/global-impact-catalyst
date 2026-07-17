CREATE TABLE IF NOT EXISTS portfolios (
    portfolio_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    archived_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_portfolios_workspace ON portfolios(workspace_id, name);
CREATE TABLE IF NOT EXISTS portfolio_memberships (
    portfolio_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    added_at TEXT NOT NULL,
    PRIMARY KEY (portfolio_id, initiative_id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(portfolio_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS draft_autosaves (
    initiative_id TEXT PRIMARY KEY,
    base_revision INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    contract_json TEXT NOT NULL
);
