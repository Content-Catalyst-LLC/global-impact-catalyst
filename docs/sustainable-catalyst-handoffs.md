# Sustainable Catalyst Handoffs

A platform handoff is a versioned, checksum-bound package created from governed repository services. v1.9.0 supports ten destinations:

- Catalyst Data
- Catalyst Analytics R
- Site Intelligence
- Workbench
- Research Lab
- Knowledge Library
- Research Librarian
- Decision Studio
- Platform Core
- Advisory

Every handoff records a destination, source workspace and initiative, handoff version, source snapshot hash, payload hash, idempotency key, status, timestamps, delivery receipt, and integration events. Destination-specific payloads retain record identifiers, method and evidence summaries, validation status, limitations, and provenance needed by the receiving product.

The receiving system must preserve governance and limitations. A valid checksum demonstrates payload identity, not truth, assurance, certification, causal proof, or fitness for a particular decision. Delivery receipts may record accepted, rejected, or failed outcomes and a remote identifier without rewriting the source package.
