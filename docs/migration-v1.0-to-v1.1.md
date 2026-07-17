# Migrating v1.0.x Records to v1.1.0

Use `migrate_legacy_record` in Python or the CLI `--migrate` option.

The migrator maps flat fields into canonical entities, recomputes derived values with the v1.1.0 engine, creates initial review and revision records, and records `source_contract_version` in provenance.

To guarantee content preservation, the complete original record is copied unchanged to:

```text
provenance.migration.legacy_record
```

This retained snapshot is the authoritative audit trail for fields that do not yet have a dedicated v1.1.0 entity mapping.

Migration may reveal validation errors that the permissive v1.0.x format did not surface. Use `--allow-invalid` to preserve such drafts while retaining their actionable issues.
