# Security, Backup, Recovery, and Release Readiness

## Security policies

Workspace policies record transport security, at-rest encryption expectations, key-rotation intervals, session timeouts, audit retention, backup encryption expectations, and additional control metadata.

## Backup and recovery

A backup plan defines schedule, retention, destination type, and encryption expectations. A backup run uses SQLite's transactionally consistent backup API, records byte size and SHA-256, and executes `PRAGMA integrity_check` against the copy.

A recovery test independently reopens the recorded backup, verifies its checksum, and stores each recovery check as governed evidence.

## Deployment environments

Development, test, staging, production, and disaster-recovery environments can record runtime versions, URLs, and control declarations. These declarations feed a release-readiness matrix but are not treated as proof unless accompanied by relevant audit or recovery records.
