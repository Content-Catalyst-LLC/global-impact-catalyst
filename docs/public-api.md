# Public and Workspace API

Global Impact Catalyst v1.9.0 exposes a stable `v1` response envelope for approved public records and permissioned workspace resources.

## Public boundary

Public endpoints return only publications whose workflow state is `published`, whose publication snapshot exists, and whose snapshot contract hash still matches the current canonical contract. Drafts, withdrawn records, stale snapshots, source contents, evidence excerpts, private reviewer information, API keys, and repository-internal records are excluded.

Public responses include an API version, resource type, generated timestamp, data, pagination where applicable, JSON-LD context, provenance identifiers, integrity hashes, and a limitations statement. Public availability is not assurance, certification, audit, factual verification, or causal proof.

## Permissioned access

Workspace endpoints require a one-time-issued API key with the needed scope. Keys are stored only as SHA-256 digests. Clients can be restricted to one workspace and assigned a per-minute request limit. Revocation is immediate. The repository records successful and denied access attempts without recording plaintext keys.

Supported scopes include `public:read`, `workspace:read`, `reports:read`, `exports:read`, `embeds:write`, `handoffs:write`, and `audit:read`.

## Reliability controls

Paginated endpoints return page, page size, total, and page count. Mutating integrations may use idempotency keys; replaying the same request returns the recorded response, while reusing a key with different content raises a conflict. API envelopes and integration records are covered by JSON Schema and release tests.
