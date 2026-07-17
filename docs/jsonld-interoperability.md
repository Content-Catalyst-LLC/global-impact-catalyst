# JSON-LD Interoperability

Public API and handoff records use a compact JSON-LD context that maps Global Impact Catalyst concepts to Schema.org, Dublin Core Terms, W3C PROV, and SDG metadata namespaces. Stable identifiers and typed relationships make records portable without pretending that external vocabularies certify the underlying impact claim.

The context maps names, descriptions, publication dates, measurement techniques, variables measured, source relationships, and derivation relationships. Consumers should preserve the supplied `@context`, source identifiers, snapshot hashes, governance status, and limitations when transforming data.
