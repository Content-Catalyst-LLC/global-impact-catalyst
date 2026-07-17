# Source Integrity and Licensing

## Integrity rules

1. Every materialized canonical source receives at least one source-version record.
2. Version records use SHA-256 and are immutable by identity.
3. Re-capturing identical content returns the existing version.
4. A supplied checksum that does not match supplied content is rejected.
5. Evidence should identify a source version whenever one is available.
6. Dataset checksums must be 64-character lowercase hexadecimal SHA-256 values.
7. Contradictory evidence remains visible in exports and integrity summaries.

## Licensing and access rights

Source and dataset records include license and access-rights fields. `not_recorded` is an explicit state, not permission to republish. Implementers must respect copyright, privacy, confidentiality, contractual restrictions, research ethics, security requirements, and applicable law.

The repository stores source metadata, checksums, and extracted evidence text supplied by an authorized user. It does not claim that storage, quotation, or redistribution is legally permitted.

## Review expectations

Before publication, reviewers should verify:

- the source can be retrieved using its locator
- the checksum corresponds to the reviewed version
- quotations are exact and properly scoped
- paraphrases preserve meaning
- dataset coverage matches the stated population, geography, and period
- license and access restrictions are respected
- supporting and contradictory evidence are represented
- the method can reasonably use the source for the asserted claim
