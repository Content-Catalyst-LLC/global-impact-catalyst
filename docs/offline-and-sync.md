# Offline Packages and Conflict-Safe Synchronization

Offline packages are governed snapshots, not independent editable databases. Each package contains exact contract and repository projections, a locale bundle, a source-state SHA-256 hash, and a package SHA-256 hash.

Offline changes enter a queue with:

- device identifier;
- entity type and stable identifier;
- operation;
- base revision;
- payload hash; and
- synchronization status.

A queued update applies only when its base revision exactly matches the current repository revision. Stale changes become explicit `revision_conflict` records and require a deliberate merge. The synchronization layer never silently overwrites newer repository state.
