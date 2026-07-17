# Evidence Chain Export

`evidence_chain(initiative_id)` produces a portable v1.3.0 view of all evidence objects associated with one initiative.

## Top-level fields

- `chain_type`: `global_impact_evidence_chain`
- `chain_version`: `1.3.0`
- `workspace_id`
- `initiative_id`
- `generated_at`
- `sources`
- `evidence_items`
- `datasets`
- `provenance_edges`
- `claim_evidence_links`
- `integrity`

Sources include their ordered version histories. The chain does not embed the full canonical contract because the contract remains available as a separate immutable repository snapshot; stable IDs join the two views.

## Integrity summary

The integrity object reports:

- counts for sources, versions, evidence items, datasets, edges, and claim links
- sources that lack a captured version/checksum
- orphan claim-evidence links
- the number of contradictory links
- a structural `valid` flag

`valid` means the repository can resolve the recorded chain. It does not mean the evidence is factually true, sufficient, unbiased, legally shareable, or adequate for a particular evaluation design.

## Export behavior

The Python service can write the chain directly to JSON. The WordPress evidence ledger can download the currently loaded chain. Workspace bundles include a workspace-wide evidence repository so backup and restore preserve the complete graph.
