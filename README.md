# Global Impact Catalyst

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, sourcing, reviewing, and transporting impact-measurement records. It combines a canonical impact-contract engine with persistent initiatives, portfolios, source records, evidence excerpts, datasets, provenance edges, claim links, audit history, and recoverable workspace bundles.

The system is not an ESG assurance platform, certification tool, audit substitute, causal-proof engine, or automatic truth system.

## v1.3.0 — Sources, Provenance, and Evidence Chain

v1.3.0 adds a governed evidence repository around the canonical v1.1.0 contract and the v1.2.0 persistence layer:

- Structured source records with title, type, locator, URL, DOI, license, access rights, and metadata
- Immutable source-version records with SHA-256 checksums and capture metadata
- Evidence excerpts, quotations, paraphrases, notes, tables, and figures
- Dataset records with version, license, checksum, schema fingerprint, coverage, and dimensions
- Directed provenance edges connecting sources and methods to observations, baselines, targets, and claims
- Explicit claim-evidence relationships: supports, contradicts, qualifies, and context
- Evidence-chain integrity summaries that expose missing versions, orphan links, and contradictory evidence
- Workspace export and restore of the complete evidence repository
- CLI and authenticated WordPress evidence-ledger workflows

The package, repository, database, evidence-chain, workspace-bundle, application, and WordPress plugin releases are v1.3.0. The canonical calculation contract remains v1.1.0 because this release does not change mathematical output or cross-runtime fixtures.

## Architecture

```text
compact authoring input
        ↓
canonical v1.1.0 contract + validation engine
        ↓
application service
        ↓
SQLite repository / CLI / WordPress repository
        ↓
initiatives + portfolios + sources + immutable source versions
        ↓
evidence items + datasets + provenance edges + claim links
        ↓
workspace bundle / evidence-chain export / backup and restore
```

Canonical contracts remain complete JSON snapshots. Evidence records are additive repository objects. A claim link never changes the calculation automatically, and contradictory evidence is preserved rather than deleted or silently averaged away.

## Python repository quick start

Initialize a local repository:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  init
```

Create and save an initiative:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  create \
  --input data/sample_global_impact_input.json \
  --generated-at 2026-07-17T18:00:00+00:00
```

The save operation materializes the contract source as a versioned source record and generates provenance edges from sources and methods to measurements and claims.

List sources for an initiative:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  sources --initiative-id gic-initiative-…
```

Add an independent source from JSON:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  add-source \
  --workspace-id gic-workspace-… \
  --initiative-id gic-initiative-… \
  --input source.json
```

Capture an immutable file version:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  add-source-version \
  --source-id gic-source-… \
  --file report.pdf \
  --label published-report \
  --mime-type application/pdf
```

Capture evidence, register a dataset, and link evidence to a claim:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 capture-evidence --source-id gic-source-… --input evidence.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 register-dataset --source-id gic-source-… --input dataset.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 link-evidence --claim-id gic-claim-… --evidence-id gic-evidence-… --relationship supports --strength direct
```

Export a complete evidence chain:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  evidence-chain \
  --initiative-id gic-initiative-… \
  --output outputs/evidence-chain.json
```

Export or restore a workspace bundle:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 export --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
python3 scripts/gic_repository.py --database outputs/restored.sqlite3 restore-bundle --input outputs/workspace-bundle.json
```

## Canonical contract CLI

The strict generator remains available:

```bash
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_contract.json \
  --markdown outputs/sample_global_impact_brief.md
```

## WordPress

Plugin folder:

```text
wordpress/global-impact-catalyst-demo/
```

Shortcodes:

```text
[global_impact_catalyst_demo]
[global_impact_catalyst_workspace]
[global_impact_catalyst_evidence_ledger]
```

The public demo is stateless. The workspace and evidence ledger require authenticated editing access. The evidence ledger can register sources, preserve checksummed versions, capture evidence, describe datasets, link evidence to claims, inspect contradictions, and export an initiative evidence chain.

## JSON Schemas and examples

- `schemas/global_impact_evidence_chain.schema.json`
- `schemas/global_impact_evidence_repository.schema.json`
- `schemas/global_impact_workspace_bundle.schema.json`
- `examples/example_global_impact_evidence_chain.json`
- `examples/example_global_impact_evidence_repository.json`
- `examples/example_global_impact_workspace_bundle.json`

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
node --check wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-evidence.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

## Repository structure

```text
app/                                  Application-facing service wrapper
contracts/                            Canonical fixtures and legacy import records
data/                                 Compact authoring sample
docs/                                 Contract, repository, evidence, migration, and WordPress docs
examples/                             Contract, evidence-chain, evidence-repository, and workspace examples
migrations/                           Versioned SQLite migration inventory
python/global_impact_core.py          Canonical v1.1.0 engine
python/global_impact_repository.py    SQLite repository and evidence chain
python/global_impact_service.py       Shared application service
schemas/                              Contract, evidence, and workspace schemas
scripts/gic_repository.py             Repository and evidence CLI
tests/                                Engine, schema, parity, repository, evidence, and integration tests
wordpress/                            Demo, workspace, and evidence-ledger plugin
```

## Methodological boundary

Global Impact Catalyst improves structure, persistence, integrity signals, reproducibility, and review visibility. A checksum demonstrates that a captured payload has not changed relative to its recorded digest; it does not prove that the source is true, authoritative, complete, unbiased, legally usable, or methodologically appropriate. Evidence links communicate declared relationships, not automatic adjudication. Human review remains required for publication and stronger claims.

## License

See `LICENSE`.
