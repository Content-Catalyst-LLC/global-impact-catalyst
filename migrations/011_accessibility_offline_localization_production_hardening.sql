CREATE TABLE IF NOT EXISTS locale_definitions (
    locale_code TEXT PRIMARY KEY,
    workspace_id TEXT,
    name TEXT NOT NULL,
    direction TEXT NOT NULL DEFAULT 'ltr',
    fallback_locale TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    translations_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_locales_workspace ON locale_definitions(workspace_id, active, locale_code);

CREATE TABLE IF NOT EXISTS offline_packages (
    package_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    locale_code TEXT NOT NULL,
    package_version TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    package_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    manifest_json TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_offline_packages_workspace ON offline_packages(workspace_id, created_at);

CREATE TABLE IF NOT EXISTS offline_change_queue (
    change_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    base_revision INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'queued',
    payload_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    conflict_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    applied_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_offline_changes_workspace ON offline_change_queue(workspace_id, status, created_at);

CREATE TABLE IF NOT EXISTS accessibility_audits (
    audit_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    surface TEXT NOT NULL,
    standard TEXT NOT NULL,
    standard_level TEXT NOT NULL,
    score REAL NOT NULL,
    status TEXT NOT NULL,
    findings_json TEXT NOT NULL,
    tested_at TEXT NOT NULL,
    tested_by TEXT NOT NULL,
    artifact_hash TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_accessibility_workspace ON accessibility_audits(workspace_id, tested_at);

CREATE TABLE IF NOT EXISTS security_policies (
    policy_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL UNIQUE,
    policy_version TEXT NOT NULL,
    encryption_at_rest_required INTEGER NOT NULL DEFAULT 1,
    transport_security_required INTEGER NOT NULL DEFAULT 1,
    minimum_key_rotation_days INTEGER NOT NULL DEFAULT 90,
    session_timeout_minutes INTEGER NOT NULL DEFAULT 60,
    audit_retention_days INTEGER NOT NULL DEFAULT 2555,
    backup_encryption_required INTEGER NOT NULL DEFAULT 1,
    settings_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS backup_plans (
    plan_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    schedule TEXT NOT NULL,
    retention_count INTEGER NOT NULL DEFAULT 7,
    destination_type TEXT NOT NULL,
    encryption_required INTEGER NOT NULL DEFAULT 1,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_backup_plans_workspace ON backup_plans(workspace_id, active);

CREATE TABLE IF NOT EXISTS backup_runs (
    backup_run_id TEXT PRIMARY KEY,
    plan_id TEXT,
    workspace_id TEXT NOT NULL,
    status TEXT NOT NULL,
    backup_path TEXT,
    backup_hash TEXT,
    byte_size INTEGER,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    verification_json TEXT NOT NULL DEFAULT '{}',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(plan_id) REFERENCES backup_plans(plan_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_backup_runs_workspace ON backup_runs(workspace_id, started_at);

CREATE TABLE IF NOT EXISTS recovery_tests (
    recovery_test_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    backup_run_id TEXT,
    status TEXT NOT NULL,
    expected_hash TEXT,
    restored_hash TEXT,
    checks_json TEXT NOT NULL,
    tested_at TEXT NOT NULL,
    tested_by TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(backup_run_id) REFERENCES backup_runs(backup_run_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_recovery_tests_workspace ON recovery_tests(workspace_id, tested_at);

CREATE TABLE IF NOT EXISTS deployment_environments (
    environment_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    environment_type TEXT NOT NULL,
    base_url TEXT,
    runtime_json TEXT NOT NULL DEFAULT '{}',
    controls_json TEXT NOT NULL DEFAULT '{}',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_deployment_workspace ON deployment_environments(workspace_id, environment_type);

CREATE TABLE IF NOT EXISTS release_readiness_checks (
    readiness_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    release_version TEXT NOT NULL,
    environment_id TEXT,
    status TEXT NOT NULL,
    score REAL NOT NULL,
    checks_json TEXT NOT NULL,
    evaluated_at TEXT NOT NULL,
    evaluated_by TEXT NOT NULL,
    artifact_hash TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    FOREIGN KEY(environment_id) REFERENCES deployment_environments(environment_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_release_readiness_workspace ON release_readiness_checks(workspace_id, evaluated_at);
