CREATE TABLE IF NOT EXISTS impact_results (
    result_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    result_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    indicator_definition_id TEXT,
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_impact_results_workspace ON impact_results(workspace_id, result_type, name);
CREATE INDEX IF NOT EXISTS idx_impact_results_initiative ON impact_results(initiative_id, result_type);

CREATE TABLE IF NOT EXISTS impact_result_relationships (
    relationship_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    from_result_id TEXT NOT NULL,
    to_result_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    contribution_weight REAL,
    notes TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(from_result_id, to_result_id, relationship_type),
    FOREIGN KEY (from_result_id) REFERENCES impact_results(result_id) ON DELETE CASCADE,
    FOREIGN KEY (to_result_id) REFERENCES impact_results(result_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_result_relationships_initiative ON impact_result_relationships(initiative_id, relationship_type);

CREATE TABLE IF NOT EXISTS observation_series (
    observation_record_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    indicator_id TEXT NOT NULL,
    indicator_definition_id TEXT,
    impact_result_id TEXT,
    period_start TEXT,
    period_end TEXT,
    period_label TEXT NOT NULL,
    value REAL,
    unit_id TEXT NOT NULL,
    data_state TEXT NOT NULL DEFAULT 'complete',
    revision_of_observation_id TEXT,
    received_at TEXT NOT NULL,
    revised_at TEXT,
    source_id TEXT,
    method_definition_id TEXT,
    dimensions_json TEXT NOT NULL,
    denominator_json TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (unit_id) REFERENCES unit_definitions(unit_id),
    FOREIGN KEY (indicator_definition_id) REFERENCES indicator_definitions(indicator_definition_id) ON DELETE SET NULL,
    FOREIGN KEY (impact_result_id) REFERENCES impact_results(result_id) ON DELETE SET NULL,
    FOREIGN KEY (revision_of_observation_id) REFERENCES observation_series(observation_record_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_observation_series_indicator ON observation_series(initiative_id, indicator_id, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_observation_series_definition ON observation_series(indicator_definition_id, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_observation_series_state ON observation_series(workspace_id, data_state, period_end);

CREATE TABLE IF NOT EXISTS beneficiary_definitions (
    beneficiary_definition_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    reach_type TEXT NOT NULL DEFAULT 'direct',
    counting_method TEXT NOT NULL DEFAULT 'unique',
    privacy_level TEXT NOT NULL DEFAULT 'aggregate_only',
    overlap_policy TEXT NOT NULL DEFAULT 'unknown',
    overlap_notes TEXT NOT NULL DEFAULT '',
    lifecycle_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_beneficiary_definitions_initiative ON beneficiary_definitions(initiative_id, name);

CREATE TABLE IF NOT EXISTS beneficiary_observations (
    beneficiary_observation_id TEXT PRIMARY KEY,
    beneficiary_definition_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    period_start TEXT,
    period_end TEXT,
    period_label TEXT NOT NULL,
    observed_count REAL,
    data_state TEXT NOT NULL DEFAULT 'complete',
    revision_of_observation_id TEXT,
    dimensions_json TEXT NOT NULL,
    overlap_estimate REAL,
    denominator_notes TEXT NOT NULL DEFAULT '',
    source_id TEXT,
    received_at TEXT NOT NULL,
    revised_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (beneficiary_definition_id) REFERENCES beneficiary_definitions(beneficiary_definition_id) ON DELETE CASCADE,
    FOREIGN KEY (revision_of_observation_id) REFERENCES beneficiary_observations(beneficiary_observation_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_beneficiary_observations_period ON beneficiary_observations(beneficiary_definition_id, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_beneficiary_observations_state ON beneficiary_observations(workspace_id, data_state);

CREATE TABLE IF NOT EXISTS financial_records (
    financial_record_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    record_type TEXT NOT NULL,
    funding_source TEXT NOT NULL DEFAULT '',
    cost_category TEXT NOT NULL DEFAULT 'uncategorized',
    period_start TEXT,
    period_end TEXT,
    period_label TEXT NOT NULL,
    amount REAL,
    currency TEXT NOT NULL,
    reporting_currency TEXT NOT NULL,
    exchange_rate REAL,
    reporting_amount REAL,
    data_state TEXT NOT NULL DEFAULT 'complete',
    source_id TEXT,
    notes TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_financial_records_initiative ON financial_records(initiative_id, record_type, period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_financial_records_currency ON financial_records(workspace_id, reporting_currency, data_state);

CREATE TABLE IF NOT EXISTS external_factors (
    external_factor_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    direction TEXT NOT NULL DEFAULT 'unknown',
    influence_level TEXT NOT NULL DEFAULT 'unknown',
    period_start TEXT,
    period_end TEXT,
    period_label TEXT NOT NULL DEFAULT '',
    source_id TEXT,
    notes TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_external_factors_initiative ON external_factors(initiative_id, period_start, period_end);

CREATE TABLE IF NOT EXISTS contribution_notes (
    contribution_note_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    impact_result_id TEXT,
    statement TEXT NOT NULL,
    contribution_type TEXT NOT NULL DEFAULT 'unknown',
    evidence_refs_json TEXT NOT NULL,
    external_factor_refs_json TEXT NOT NULL,
    limitations TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (impact_result_id) REFERENCES impact_results(result_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_contribution_notes_initiative ON contribution_notes(initiative_id, impact_result_id);

CREATE TABLE IF NOT EXISTS outcome_portfolios (
    outcome_portfolio_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    aggregation_method TEXT NOT NULL DEFAULT 'sum',
    target_unit_id TEXT,
    period_policy TEXT NOT NULL DEFAULT 'exact',
    overlap_policy TEXT NOT NULL DEFAULT 'exclude_unknown_or_overlapping',
    missing_data_policy TEXT NOT NULL DEFAULT 'exclude_and_disclose',
    archived_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (target_unit_id) REFERENCES unit_definitions(unit_id)
);
CREATE INDEX IF NOT EXISTS idx_outcome_portfolios_workspace ON outcome_portfolios(workspace_id, name);

CREATE TABLE IF NOT EXISTS outcome_portfolio_memberships (
    outcome_portfolio_id TEXT NOT NULL,
    membership_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    indicator_id TEXT NOT NULL,
    indicator_definition_id TEXT,
    impact_result_id TEXT,
    population_scope TEXT NOT NULL DEFAULT '',
    overlap_group TEXT NOT NULL DEFAULT '',
    denominator_definition TEXT NOT NULL DEFAULT '',
    weight REAL NOT NULL DEFAULT 1.0,
    position INTEGER NOT NULL DEFAULT 0,
    added_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    PRIMARY KEY (outcome_portfolio_id, membership_id),
    FOREIGN KEY (outcome_portfolio_id) REFERENCES outcome_portfolios(outcome_portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (indicator_definition_id) REFERENCES indicator_definitions(indicator_definition_id) ON DELETE SET NULL,
    FOREIGN KEY (impact_result_id) REFERENCES impact_results(result_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_outcome_portfolio_members ON outcome_portfolio_memberships(outcome_portfolio_id, position);

CREATE TABLE IF NOT EXISTS portfolio_aggregation_runs (
    aggregation_run_id TEXT PRIMARY KEY,
    outcome_portfolio_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    period_start TEXT,
    period_end TEXT,
    period_label TEXT NOT NULL DEFAULT '',
    aggregation_method TEXT NOT NULL,
    target_unit_id TEXT,
    result_value REAL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    FOREIGN KEY (outcome_portfolio_id) REFERENCES outcome_portfolios(outcome_portfolio_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_portfolio_aggregation_runs ON portfolio_aggregation_runs(outcome_portfolio_id, created_at);
