CREATE TABLE IF NOT EXISTS analysis_benchmarks (
    benchmark_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, indicator_id TEXT NOT NULL,
    indicator_definition_id TEXT, name TEXT NOT NULL, benchmark_type TEXT NOT NULL DEFAULT 'external',
    value REAL NOT NULL, unit_id TEXT NOT NULL, period_start TEXT, period_end TEXT,
    period_label TEXT NOT NULL DEFAULT '', geography TEXT NOT NULL DEFAULT '', population TEXT NOT NULL DEFAULT '',
    source_id TEXT, method_definition_id TEXT, quality_status TEXT NOT NULL DEFAULT 'not_assessed',
    lifecycle_status TEXT NOT NULL DEFAULT 'draft', revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analysis_benchmarks_workspace ON analysis_benchmarks(workspace_id, indicator_id, period_label);
CREATE TABLE IF NOT EXISTS analysis_comparison_sets (
    comparison_set_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '', indicator_id TEXT NOT NULL, indicator_definition_id TEXT,
    comparison_policy_json TEXT NOT NULL, lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analysis_comparison_members (
    comparison_member_id TEXT PRIMARY KEY, comparison_set_id TEXT NOT NULL,
    initiative_id TEXT, benchmark_id TEXT, label TEXT NOT NULL, geography TEXT NOT NULL DEFAULT '',
    population TEXT NOT NULL DEFAULT '', period_label TEXT NOT NULL DEFAULT '', value_override REAL,
    unit_id TEXT, metadata_json TEXT NOT NULL,
    FOREIGN KEY (comparison_set_id) REFERENCES analysis_comparison_sets(comparison_set_id) ON DELETE CASCADE,
    FOREIGN KEY (benchmark_id) REFERENCES analysis_benchmarks(benchmark_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_analysis_comparison_members_set ON analysis_comparison_members(comparison_set_id, label);
CREATE TABLE IF NOT EXISTS analysis_scenarios (
    scenario_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, initiative_id TEXT NOT NULL,
    indicator_id TEXT NOT NULL, indicator_definition_id TEXT, name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '', scenario_type TEXT NOT NULL DEFAULT 'projection',
    model_type TEXT NOT NULL DEFAULT 'linear', unit_id TEXT NOT NULL, start_period TEXT NOT NULL DEFAULT '',
    end_period TEXT NOT NULL DEFAULT '', periods INTEGER NOT NULL DEFAULT 1, base_value REAL,
    parameters_json TEXT NOT NULL, assumptions_json TEXT NOT NULL, limitations_json TEXT NOT NULL,
    source_id TEXT, method_definition_id TEXT, target_model_id TEXT,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft', revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analysis_scenarios_workspace ON analysis_scenarios(workspace_id, initiative_id, indicator_id);
CREATE TABLE IF NOT EXISTS analysis_uncertainty_models (
    uncertainty_model_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, name TEXT NOT NULL,
    uncertainty_type TEXT NOT NULL, confidence_level REAL NOT NULL DEFAULT 0.95,
    absolute_margin REAL, relative_margin_percent REAL, lower_bound REAL, upper_bound REAL,
    distribution TEXT NOT NULL DEFAULT 'bounded', assumptions_json TEXT NOT NULL,
    limitations_json TEXT NOT NULL, source_id TEXT, method_definition_id TEXT,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft', revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS analysis_runs (
    analysis_run_id TEXT PRIMARY KEY, workspace_id TEXT NOT NULL, initiative_id TEXT,
    analysis_type TEXT NOT NULL, subject_id TEXT NOT NULL, input_hash TEXT NOT NULL,
    result_hash TEXT NOT NULL, result_json TEXT NOT NULL, created_by TEXT NOT NULL,
    created_at TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_subject ON analysis_runs(analysis_type, subject_id, created_at);
CREATE TABLE IF NOT EXISTS analysis_sensitivity_runs (
    sensitivity_run_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL, workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL, parameter_name TEXT NOT NULL, baseline_value REAL NOT NULL,
    low_value REAL NOT NULL, high_value REAL NOT NULL, low_result REAL NOT NULL,
    baseline_result REAL NOT NULL, high_result REAL NOT NULL, absolute_effect REAL NOT NULL,
    relative_effect_percent REAL, rank_order INTEGER NOT NULL DEFAULT 0, created_by TEXT NOT NULL,
    created_at TEXT NOT NULL, metadata_json TEXT NOT NULL,
    FOREIGN KEY (scenario_id) REFERENCES analysis_scenarios(scenario_id) ON DELETE CASCADE
);
