# Reproducible Export Bundles

The v1.8.0 reproducible export format is designed for review, archiving, institutional handoff, and independent byte-level verification.

## Bundle contents

A bundle always contains `manifest.json`, `SHA256SUMS.txt`, and `workspace-bundle.json`. When a report is selected, it also contains structured JSON, Markdown, accessible HTML, citations, and a methodology appendix. When a publication snapshot is selected, the exact snapshot is included.

## Determinism

ZIP entries are sorted and use a fixed 1980 timestamp. Dynamic export timestamps and export-history records are normalized in the embedded workspace bundle. Audit and operational export history are excluded from the deterministic source image. Governance records, contract revisions, evidence versions, report content, and publication hashes remain intact.

## Verification

`verify_reproducible_export` checks every artifact listed in the manifest and reports missing files or checksum mismatches. The archive SHA-256 identifies the complete ZIP. Checksum validity proves byte identity only; it does not prove the truth, quality, or causal validity of the underlying claims.
