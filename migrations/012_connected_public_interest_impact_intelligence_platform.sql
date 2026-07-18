CREATE TABLE IF NOT EXISTS institutions (
    institution_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    mission TEXT NOT NULL DEFAULT '',
    governance_model TEXT NOT NULL DEFAULT 'public_interest',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS institution_members (
    membership_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    display_name TEXT NOT NULL DEFAULT '',
    email_hash TEXT,
    role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    permissions_json TEXT NOT NULL DEFAULT '[]',
    joined_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(institution_id, principal_id),
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_institution_members_role ON institution_members(institution_id, role, status);

CREATE TABLE IF NOT EXISTS institution_workspaces (
    link_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    relationship TEXT NOT NULL DEFAULT 'owned',
    status TEXT NOT NULL DEFAULT 'active',
    policy_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(institution_id, workspace_id),
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_institution_workspaces_workspace ON institution_workspaces(workspace_id, status);

CREATE TABLE IF NOT EXISTS platform_connections (
    connection_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    destination TEXT NOT NULL,
    connection_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'configured',
    contract_version TEXT NOT NULL,
    capabilities_json TEXT NOT NULL DEFAULT '[]',
    config_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_verified_at TEXT,
    verification_json TEXT NOT NULL DEFAULT '{}',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(institution_id, destination, connection_type),
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS decision_pathways (
    pathway_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    nodes_json TEXT NOT NULL DEFAULT '[]',
    edges_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_decision_pathways_workspace ON decision_pathways(workspace_id, status);

CREATE TABLE IF NOT EXISTS platform_workflows (
    workflow_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    trigger_type TEXT NOT NULL DEFAULT 'manual',
    steps_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_platform_workflows_workspace ON platform_workflows(workspace_id, status);

CREATE TABLE IF NOT EXISTS platform_workflow_runs (
    run_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    status TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    output_hash TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    step_results_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(workflow_id) REFERENCES platform_workflows(workflow_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_platform_runs_workflow ON platform_workflow_runs(workflow_id, started_at);

CREATE TABLE IF NOT EXISTS platform_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    status TEXT NOT NULL,
    source_hashes_json TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    snapshot_hash TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_platform_snapshots_workspace ON platform_snapshots(workspace_id, generated_at);

CREATE TABLE IF NOT EXISTS platform_events (
    event_id TEXT PRIMARY KEY,
    institution_id TEXT,
    workspace_id TEXT,
    event_type TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    correlation_id TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(institution_id) REFERENCES institutions(institution_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_platform_events_workspace ON platform_events(workspace_id, occurred_at);
CREATE INDEX IF NOT EXISTS idx_platform_events_correlation ON platform_events(correlation_id, occurred_at);
