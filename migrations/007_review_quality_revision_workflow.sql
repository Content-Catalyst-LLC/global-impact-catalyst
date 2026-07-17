CREATE TABLE IF NOT EXISTS workflow_roles (
    role_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    permissions_json TEXT NOT NULL,
    is_system INTEGER NOT NULL DEFAULT 0,
    archived_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_workflow_roles_name ON workflow_roles(workspace_id, name);

CREATE TABLE IF NOT EXISTS review_assignments (
    assignment_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    priority TEXT NOT NULL DEFAULT 'normal',
    due_at TEXT,
    assigned_by TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES workflow_roles(role_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_review_assignments_workspace ON review_assignments(workspace_id, status, due_at);
CREATE INDEX IF NOT EXISTS idx_review_assignments_subject ON review_assignments(subject_type, subject_id, status);
CREATE INDEX IF NOT EXISTS idx_review_assignments_reviewer ON review_assignments(reviewer_id, status, due_at);

CREATE TABLE IF NOT EXISTS review_comments (
    comment_id TEXT PRIMARY KEY,
    assignment_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    parent_comment_id TEXT,
    visibility TEXT NOT NULL DEFAULT 'workspace',
    body TEXT NOT NULL,
    resolution_status TEXT NOT NULL DEFAULT 'open',
    resolved_by TEXT,
    resolved_at TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES review_assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES review_comments(comment_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_review_comments_assignment ON review_comments(assignment_id, resolution_status, created_at);
CREATE INDEX IF NOT EXISTS idx_review_comments_subject ON review_comments(subject_type, subject_id, resolution_status);

CREATE TABLE IF NOT EXISTS quality_assessments (
    assessment_id TEXT PRIMARY KEY,
    assignment_id TEXT,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    rubric_id TEXT NOT NULL,
    rubric_version TEXT NOT NULL,
    assessor_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    score REAL NOT NULL,
    maximum_score REAL NOT NULL,
    grade TEXT NOT NULL,
    dimensions_json TEXT NOT NULL,
    findings_json TEXT NOT NULL,
    limitations TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    submitted_at TEXT,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES review_assignments(assignment_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_subject ON quality_assessments(subject_type, subject_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_assignment ON quality_assessments(assignment_id, status);

CREATE TABLE IF NOT EXISTS approval_decisions (
    decision_id TEXT PRIMARY KEY,
    assignment_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    conditions_json TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    supersedes_decision_id TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (assignment_id) REFERENCES review_assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (supersedes_decision_id) REFERENCES approval_decisions(decision_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_approval_decisions_subject ON approval_decisions(subject_type, subject_id, decided_at);
CREATE INDEX IF NOT EXISTS idx_approval_decisions_assignment ON approval_decisions(assignment_id, decided_at);

CREATE TABLE IF NOT EXISTS workflow_revisions (
    workflow_revision_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    revision_number INTEGER NOT NULL,
    change_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    previous_content_hash TEXT,
    content_hash TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    UNIQUE(subject_type, subject_id, revision_number)
);
CREATE INDEX IF NOT EXISTS idx_workflow_revisions_subject ON workflow_revisions(subject_type, subject_id, revision_number);
CREATE INDEX IF NOT EXISTS idx_workflow_revisions_workspace ON workflow_revisions(workspace_id, created_at);

CREATE TABLE IF NOT EXISTS correction_records (
    correction_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'minor',
    status TEXT NOT NULL DEFAULT 'open',
    reason TEXT NOT NULL,
    proposed_changes_json TEXT NOT NULL,
    opened_by TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    applied_by TEXT,
    applied_at TEXT,
    resulting_revision_id TEXT,
    resolution_notes TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (resulting_revision_id) REFERENCES workflow_revisions(workflow_revision_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_corrections_subject ON correction_records(subject_type, subject_id, status, opened_at);

CREATE TABLE IF NOT EXISTS publication_records (
    publication_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    initiative_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    title TEXT NOT NULL,
    publication_status TEXT NOT NULL DEFAULT 'draft',
    release_label TEXT NOT NULL DEFAULT '',
    public_url TEXT NOT NULL DEFAULT '',
    approved_decision_id TEXT,
    quality_assessment_id TEXT,
    content_hash TEXT NOT NULL,
    published_revision_id TEXT,
    published_at TEXT,
    published_by TEXT,
    withdrawn_at TEXT,
    withdrawn_by TEXT,
    withdrawal_reason TEXT NOT NULL DEFAULT '',
    supersedes_publication_id TEXT,
    revision INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    FOREIGN KEY (approved_decision_id) REFERENCES approval_decisions(decision_id) ON DELETE SET NULL,
    FOREIGN KEY (quality_assessment_id) REFERENCES quality_assessments(assessment_id) ON DELETE SET NULL,
    FOREIGN KEY (published_revision_id) REFERENCES workflow_revisions(workflow_revision_id) ON DELETE SET NULL,
    FOREIGN KEY (supersedes_publication_id) REFERENCES publication_records(publication_id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_publications_subject ON publication_records(subject_type, subject_id, publication_status, updated_at);
CREATE INDEX IF NOT EXISTS idx_publications_workspace ON publication_records(workspace_id, publication_status, published_at);

CREATE TABLE IF NOT EXISTS publication_events (
    publication_event_id TEXT PRIMARY KEY,
    publication_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    event_at TEXT NOT NULL,
    details_json TEXT NOT NULL,
    FOREIGN KEY (publication_id) REFERENCES publication_records(publication_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_publication_events ON publication_events(publication_id, event_at);
