CREATE TABLE IF NOT EXISTS unit_definitions (
    unit_id TEXT PRIMARY KEY,
    workspace_id TEXT,
    code TEXT NOT NULL,
    symbol TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    dimension TEXT NOT NULL,
    canonical_unit_id TEXT,
    scale_to_canonical REAL NOT NULL DEFAULT 1.0,
    offset_to_canonical REAL NOT NULL DEFAULT 0.0,
    precision_digits INTEGER NOT NULL DEFAULT 2,
    lifecycle_status TEXT NOT NULL DEFAULT 'active',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_units_workspace_code ON unit_definitions(COALESCE(workspace_id,''), code);
CREATE INDEX IF NOT EXISTS idx_units_dimension ON unit_definitions(dimension, code);

CREATE TABLE IF NOT EXISTS indicator_definitions (
    indicator_definition_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    direction TEXT NOT NULL DEFAULT 'higher_is_better',
    unit_id TEXT NOT NULL,
    aggregation_method TEXT NOT NULL DEFAULT 'latest',
    formula_expression TEXT NOT NULL DEFAULT '',
    formula_language TEXT NOT NULL DEFAULT 'gic-expression-1.0',
    disaggregation_json TEXT NOT NULL,
    quality_profile_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    current_version INTEGER NOT NULL DEFAULT 0,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES unit_definitions(unit_id)
);
CREATE INDEX IF NOT EXISTS idx_indicator_definitions_workspace ON indicator_definitions(workspace_id, name);
CREATE INDEX IF NOT EXISTS idx_indicator_definitions_unit ON indicator_definitions(unit_id);

CREATE TABLE IF NOT EXISTS indicator_definition_versions (
    indicator_definition_version_id TEXT PRIMARY KEY,
    indicator_definition_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    version_label TEXT NOT NULL,
    effective_from TEXT,
    effective_through TEXT,
    definition_hash TEXT NOT NULL,
    definition_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    UNIQUE(indicator_definition_id, version_number),
    UNIQUE(indicator_definition_id, definition_hash),
    FOREIGN KEY (indicator_definition_id) REFERENCES indicator_definitions(indicator_definition_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_indicator_definition_versions ON indicator_definition_versions(indicator_definition_id, version_number);

CREATE TABLE IF NOT EXISTS baseline_models (
    baseline_model_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    method_type TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    period_start TEXT,
    period_end TEXT,
    rolling_periods INTEGER,
    benchmark_value REAL,
    formula_expression TEXT NOT NULL DEFAULT '',
    formula_language TEXT NOT NULL DEFAULT 'gic-expression-1.0',
    minimum_observations INTEGER NOT NULL DEFAULT 1,
    confidence TEXT NOT NULL DEFAULT 'medium',
    parameters_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    current_version INTEGER NOT NULL DEFAULT 0,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES unit_definitions(unit_id)
);
CREATE INDEX IF NOT EXISTS idx_baseline_models_workspace ON baseline_models(workspace_id, name);

CREATE TABLE IF NOT EXISTS baseline_model_versions (
    baseline_model_version_id TEXT PRIMARY KEY,
    baseline_model_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    version_label TEXT NOT NULL,
    model_hash TEXT NOT NULL,
    model_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    UNIQUE(baseline_model_id, version_number),
    UNIQUE(baseline_model_id, model_hash),
    FOREIGN KEY (baseline_model_id) REFERENCES baseline_models(baseline_model_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS target_models (
    target_model_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    indicator_definition_id TEXT,
    name TEXT NOT NULL,
    target_type TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    direction TEXT NOT NULL DEFAULT 'higher_is_better',
    target_value REAL,
    lower_value REAL,
    upper_value REAL,
    relative_change_percent REAL,
    start_period TEXT,
    end_period TEXT,
    start_value REAL,
    end_value REAL,
    trajectory_type TEXT NOT NULL DEFAULT 'linear',
    formula_expression TEXT NOT NULL DEFAULT '',
    formula_language TEXT NOT NULL DEFAULT 'gic-expression-1.0',
    milestones_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    current_version INTEGER NOT NULL DEFAULT 0,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (indicator_definition_id) REFERENCES indicator_definitions(indicator_definition_id) ON DELETE SET NULL,
    FOREIGN KEY (unit_id) REFERENCES unit_definitions(unit_id)
);
CREATE INDEX IF NOT EXISTS idx_target_models_workspace ON target_models(workspace_id, name);
CREATE INDEX IF NOT EXISTS idx_target_models_indicator ON target_models(indicator_definition_id);

CREATE TABLE IF NOT EXISTS target_model_versions (
    target_model_version_id TEXT PRIMARY KEY,
    target_model_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    version_label TEXT NOT NULL,
    model_hash TEXT NOT NULL,
    model_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    UNIQUE(target_model_id, version_number),
    UNIQUE(target_model_id, model_hash),
    FOREIGN KEY (target_model_id) REFERENCES target_models(target_model_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS method_definitions (
    method_definition_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    method_kind TEXT NOT NULL DEFAULT 'measurement',
    design_type TEXT NOT NULL DEFAULT 'monitoring',
    description TEXT NOT NULL DEFAULT '',
    formula_expression TEXT NOT NULL DEFAULT '',
    formula_language TEXT NOT NULL DEFAULT 'gic-expression-1.0',
    input_requirements_json TEXT NOT NULL,
    quality_profile_json TEXT NOT NULL,
    limitations_json TEXT NOT NULL,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    current_version INTEGER NOT NULL DEFAULT 0,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_method_definitions_workspace ON method_definitions(workspace_id, name);

CREATE TABLE IF NOT EXISTS method_definition_versions (
    method_definition_version_id TEXT PRIMARY KEY,
    method_definition_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    version_label TEXT NOT NULL,
    method_hash TEXT NOT NULL,
    method_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    UNIQUE(method_definition_id, version_number),
    UNIQUE(method_definition_id, method_hash),
    FOREIGN KEY (method_definition_id) REFERENCES method_definitions(method_definition_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS indicator_registry_bindings (
    binding_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    indicator_id TEXT NOT NULL,
    indicator_definition_id TEXT NOT NULL,
    indicator_definition_version_id TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    baseline_model_id TEXT,
    baseline_model_version_id TEXT,
    target_model_id TEXT,
    target_model_version_id TEXT,
    method_definition_id TEXT,
    method_definition_version_id TEXT,
    bound_at TEXT NOT NULL,
    bound_by TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    metadata_json TEXT NOT NULL,
    UNIQUE(initiative_id, indicator_id),
    FOREIGN KEY (indicator_definition_id) REFERENCES indicator_definitions(indicator_definition_id),
    FOREIGN KEY (indicator_definition_version_id) REFERENCES indicator_definition_versions(indicator_definition_version_id),
    FOREIGN KEY (unit_id) REFERENCES unit_definitions(unit_id),
    FOREIGN KEY (baseline_model_id) REFERENCES baseline_models(baseline_model_id) ON DELETE SET NULL,
    FOREIGN KEY (target_model_id) REFERENCES target_models(target_model_id) ON DELETE SET NULL,
    FOREIGN KEY (method_definition_id) REFERENCES method_definitions(method_definition_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_indicator_bindings_workspace ON indicator_registry_bindings(workspace_id, initiative_id);
