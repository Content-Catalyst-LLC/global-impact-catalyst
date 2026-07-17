# Sources, Provenance, and Evidence Repository

Global Impact Catalyst v1.3.0 introduces an additive evidence repository around canonical impact contracts. It is designed to answer four distinct questions without collapsing them into one field:

1. **What source was used?** A structured source record identifies the document, dataset, internal record, interview, instrument, or other material.
2. **Which exact version was used?** A source-version record preserves a checksum and capture metadata.
3. **What evidence was extracted?** An evidence item stores a quotation, excerpt, paraphrase, note, table, figure, or dataset excerpt with a locator.
4. **How was it used?** Provenance edges and claim-evidence links state how material informs measurements and claims.

## Source records

A source record contains a stable `source_id`, workspace and initiative scope, title, type, locator, URL, DOI, license, access rights, lifecycle status, revision, timestamps, and extensible metadata. Source identity is separate from source versioning. Editing a citation or access-rights statement does not overwrite a captured source payload.

## Source versions and checksums

Each source version includes:

- stable `source_version_id`
- monotonically increasing version number
- human-readable version label
- content hash
- checksum algorithm and checksum value
- MIME type and optional byte size
- capture timestamp and actor
- metadata such as the original filename

v1.3.0 supports SHA-256. A repeated payload is idempotent: the repository returns the existing version rather than creating a duplicate. When a caller supplies both a payload and an expected checksum, a mismatch is rejected.

A checksum is an integrity signal, not a truth or authenticity determination. It cannot establish authorship, legal admissibility, representativeness, or methodological quality.

## Evidence items

Evidence items are linked to a source and, when available, a specific source version. Supported evidence types are:

- excerpt
- quotation
- dataset excerpt
- observation note
- document note
- table
- figure

An evidence item requires at least one of an exact quotation, paraphrase, or note. Page, character, section, table, or other locator data may be recorded. The normalized content receives its own SHA-256 content hash.

## Datasets

Dataset records preserve a durable reference to data used in an impact record. A dataset may include:

- title and version
- landing page and distribution URL
- license
- SHA-256 checksum
- schema fingerprint
- temporal and spatial coverage
- row and column counts
- extensible metadata

The repository stores metadata and integrity identifiers; it does not silently ingest or redistribute restricted data.

## Provenance edges

The provenance graph uses directed edges:

```text
subject -- predicate --> object
```

Examples:

```text
source -- supports --> observation
method -- produced --> observation
observation -- informs_claim --> claim
source -- informs_claim --> claim
```

Each edge records workspace and initiative scope, process name, optional method and method version, time, actor, and metadata. Deterministic edge IDs make repeated contract materialization idempotent.

## Claim-evidence relationships

Evidence items may be explicitly related to claims as:

- `supports`
- `contradicts`
- `qualifies`
- `context`

Strength may be `direct`, `indirect`, or `contextual`. Contradictory evidence is retained and counted. The repository does not delete, hide, or automatically neutralize it.

## Contract compatibility

The canonical contract remains v1.1.0. Its existing source, method, measurement, and claim identifiers serve as stable anchors. v1.3.0 materializes these identifiers into the repository and adds evidence objects around them. This prevents repository enrichment from changing established calculations or cross-runtime parity.
