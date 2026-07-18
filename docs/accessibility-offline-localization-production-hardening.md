# Accessibility, Offline Use, Localization, and Production Hardening

Global Impact Catalyst v1.10.0 adds a governed production repository without changing the canonical v1.1.0 calculation contract.

## Production repository

The v1.10.0 production repository records:

- locale definitions and fallback chains;
- hash-bound offline workspace packages;
- queued offline changes and explicit revision conflicts;
- accessibility audits and remediation findings;
- workspace security policies;
- backup plans, verified backup runs, and recovery tests;
- deployment environments; and
- release-readiness evaluations.

These records are exported inside the v1.10.0 workspace bundle and restored in dependency order.

## Boundaries

An accessibility audit is an evidence record, not independent accessibility certification. A passing backup integrity check proves that a SQLite backup can be opened and matches its recorded checksum; it does not prove every external dependency has been recovered. Security policy records describe configured expectations and do not guarantee absence of compromise.

## Release blocking

A production readiness decision is `ready` only when all required checks pass:

1. database schema 11 is active;
2. transport and at-rest security requirements are enabled;
3. a passing accessibility audit exists;
4. a verified recovery test exists;
5. at least one active locale is available; and
6. the repository release contract passes.
