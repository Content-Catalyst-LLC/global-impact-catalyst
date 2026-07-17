# Global Impact Catalyst

Global Impact Catalyst is an open, reproducible impact-contract and validation engine for Sustainable Catalyst. It converts compact authoring inputs into durable, versioned contracts that preserve entered facts, derived metrics, evidence references, methods, claim boundaries, validation issues, review state, revisions, and publication metadata.

The system is not a proprietary ESG platform, certification tool, assurance product, audit substitute, causal-proof engine, or automatic truth system. It is public-interest infrastructure for making impact records inspectable and portable.

## v1.1.0 — Canonical Impact Contract and Validation Engine

v1.1.0 replaces the flat output record with a canonical entity-oriented contract. It adds:

- Stable deterministic IDs and timestamps for material entities
- `contract_version`, `schema_version`, `record_id`, lifecycle state, and provenance
- Explicit separation between entered `facts` and reproducible `derived` values
- Structured validation issues with severity, JSON-style path, rule ID, message, and remediation
- Semantic validation for required facts, units, periods, indicator direction, target compatibility, sources, and methods
- Governed claim types from descriptive observation through causal claim
- Evidence and design gates for comparison, contribution, and causal language
- Lossless migration from v1.0.x flat records
- Strict schemas for authoring inputs, canonical contracts, and validation results
- Fifteen exact Python/browser golden fixtures
- An expanded WordPress contract builder and validation interface

## Canonical contract layers

```text
compact authoring input
        ↓ normalize
entered facts + stable entity identity
        ↓ validate
structured errors, warnings, and remediation
        ↓ derive
metrics, interpretations, and claim eligibility
        ↓ govern
reviews, revisions, publications, provenance, boundaries
        ↓ export
canonical JSON contract + Markdown brief
```

The root contract keys are:

```text
contract_type
contract_version
schema_version
record_id
created_at / updated_at
lifecycle_status
provenance
facts
  workspace / initiative / goal / outcomes / indicator
  measurement / sources / methods / populations / geographies / budgets
derived
  metrics / interpretations / claims
governance
  reviews / revisions / publications
validation
traceability_path
boundaries
```

See `docs/canonical-impact-contract.md` for field definitions.

## WordPress demo

Plugin folder:

```text
wordpress/global-impact-catalyst-demo/
```

Shortcode:

```text
[global_impact_catalyst_demo]
```

The browser demo builds the same contract shape as Python and applies the same validation and claim rules. Multiple shortcode instances can appear on one page without duplicate HTML IDs.

## Python quick start

Generate a strict contract. The command exits with status `2` if semantic errors are present:

```bash
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_contract.json \
  --markdown outputs/sample_global_impact_brief.md
```

Allow an invalid draft to be written with its validation issues attached:

```bash
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_contract.json \
  --allow-invalid
```

Migrate a v1.0.x flat record without discarding its original content:

```bash
python3 python/global_impact_core.py \
  --input contracts/legacy/legacy-v1.0.1-record.json \
  --output outputs/migrated-v1.1.0-contract.json \
  --migrate \
  --allow-invalid
```

For reproducible builds, provide a fixed timestamp:

```bash
--generated-at 2026-07-17T18:00:00+00:00
```

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

Validation issues use this shape:

```json
{
  "issue_id": "gic-issue-…",
  "severity": "error",
  "path": "$.facts.measurement.target.value",
  "rule_id": "GIC-DIRECTION-001",
  "message": "A higher-is-better indicator has a target below its baseline.",
  "remediation": "Change the direction to lower-is-better or correct the target."
}
```

See `docs/validation-rules.md` for the rule catalog.

## Claim governance

Supported claim types:

1. `descriptive_observation`
2. `progress_to_target_statement`
3. `comparison`
4. `contribution_statement`
5. `causal_claim`

Stronger claim types require explicit claim text and additional design metadata. Causal claims require a quasi-experimental or randomized design, causal design documentation, high confidence, and reviewed or published status. A contract may still be exported as a draft when a claim is blocked, but its validation and claim eligibility state remain attached.

## Cross-runtime parity

The Python and browser implementations are independently executable and governed by complete fixtures in `contracts/fixtures/`. Every fixture contains compact input, a fixed timestamp, and the entire expected canonical contract. Exact output parity includes IDs, fingerprints, issue IDs, metrics, entity order, claim eligibility, boundaries, and governance data.

## Repository structure

```text
app/                         Application-facing wrapper
app/tests/                   Wrapper tests
contracts/fixtures/          Canonical cross-runtime golden fixtures
contracts/legacy/            Legacy migration fixture
python/                      Canonical Python contract engine
schemas/                     Input, contract, compatibility, and validation schemas
data/                        Canonical authoring sample
examples/                    Generated contract and Markdown brief
docs/                        Contract, validation, methodology, migration, and review docs
scripts/                     Fixture, parity, release, WordPress, and smoke checks
tests/                       Core, schema, parity, and WordPress tests
wordpress/global-impact-catalyst-demo/  WordPress shortcode plugin
release/                     Version-specific release notes
.github/workflows/           Continuous integration
outputs/                     Local generated outputs
```

## Methodological boundary

Global Impact Catalyst improves structure, reproducibility, and review visibility. It does not prove that entered data is accurate, that a source is authentic, that a method is appropriate, that an intervention caused an outcome, or that a public claim satisfies legal, accounting, evaluation, regulatory, or assurance requirements.

## License

See `LICENSE`. Review applicable legal, privacy, ethical, evaluation, data-governance, and reporting obligations before formal use.
