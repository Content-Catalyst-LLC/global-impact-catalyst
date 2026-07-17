# Review, Quality, and Revision Workflow

Global Impact Catalyst v1.6.0 adds a governed human-review layer around the canonical contract, evidence repository, indicator registry, and measurement repository.

## Workflow objects

- **Workflow roles** define workspace-scoped permissions. Five default roles are materialized for each workspace: Program Owner, Evidence Reviewer, Methods Reviewer, Approver, and Publisher.
- **Review assignments** bind a reviewer and role to a versioned subject such as a contract, evidence repository, registry, measurement repository, observation, or impact result.
- **Review comments** support threads, visibility controls, and explicit resolution states.
- **Quality assessments** apply weighted rubric dimensions and preserve the findings that produced the score.
- **Approval decisions** are append-only decisions that may approve, request changes, reject, or abstain.
- **Workflow revisions** preserve immutable JSON snapshots and SHA-256 hashes for every saved contract revision.
- **Corrections** identify a reason, severity, proposed change, resolution, and resulting revision.
- **Publications** bind approved content to a quality assessment and immutable revision. Withdrawal never erases the publication or its events.

## Core gates

Approval is blocked when comments remain open, no submitted quality assessment exists, or the latest assessment is below the adequate threshold. Publication is blocked without approval, adequate quality, resolved corrections, and an unchanged content hash.

## Compatibility

The canonical calculation contract remains v1.1.0. Evidence remains v1.3.0, the indicator registry remains v1.4.0, and the measurement repository remains v1.5.0. v1.6.0 changes governance and persistence, not metric semantics.
