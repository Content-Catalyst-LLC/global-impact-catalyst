# Global Impact Catalyst

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, sourcing, governing, measuring, reviewing, and publishing impact records. It combines a canonical impact contract with persistent initiatives, evidence provenance, governed indicator definitions, multi-period observations, aggregate beneficiary records, program finances, guarded outcome portfolios, and auditable review workflows.

The system is not an ESG assurance platform, certification tool, audit substitute, causal-proof engine, regulatory filing system, or automatic truth system.

## v1.7.0 governance workflow — Review, Quality, and Revision Workflow

v1.6.0 adds governed review and publication operations around the existing contract, evidence, registry, and measurement layers:

- Workspace-scoped review roles and permissions
- Review assignments with priority, due date, scope, and status
- Threaded comments with explicit resolution states
- Weighted quality assessments and descriptive grades
- Approval, change-request, rejection, and abstention decisions
- Approval gates for unresolved comments and inadequate quality review
- Immutable contract snapshots, immutable revision history, and SHA-256 lineage
- Correction records linked to resulting revisions
- Publication drafts bound to exact content hashes
- Approval, quality, correction, and stale-content publication gates
- Published, withdrawn, and superseded lifecycle history
- Review-workflow export, schema validation, backup, and lossless restore
- Python service, CLI, and authenticated WordPress review interface

Compatibility identities remain explicit: canonical contract v1.1.0, evidence repository v1.3.0, indicator registry v1.4.0, measurement repository v1.5.0, and review workflow/workspace bundle v1.6.0. Database schema version is 7.

## Architecture

```text
compact authoring input
        ↓
canonical v1.1.0 contract + validation engine
        ↓
application service
        ↓
SQLite repository / CLI / WordPress repository
        ├── initiatives + autosaves + audit history
        ├── sources + versions + evidence + datasets + provenance
        ├── units + indicators + baselines + targets + methods
        ├── results + observations + beneficiaries + finances + outcome portfolios
        └── roles + assignments + comments + quality + decisions + corrections + publications
                                      ↓
 workspace bundle / evidence export / registry export / measurement export / review export / backup
```

Canonical contracts remain complete JSON snapshots. Evidence, registry, measurement, and review records are additive governed repository objects. Observation changes create revision lineage; registry updates create immutable versions; contract saves create workflow revision snapshots; published records remain tied to the exact reviewed content hash.

## Python repository quick start

Initialize a repository and create an initiative:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 init
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 create \
  --input data/sample_global_impact_input.json \
  --generated-at 2026-07-17T18:00:00+00:00
```

Create a review assignment and inspect the workflow:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 assign-review \
  --workspace-id gic-workspace-… \
  --initiative-id gic-initiative-… \
  --input review-assignment.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 review-workflow \
  --workspace-id gic-workspace-… \
  --output outputs/review-workflow.json
```

Record quality and a decision:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 assess-quality \
  --workspace-id gic-workspace-… --initiative-id gic-initiative-… --input quality-assessment.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 review-decision \
  --workspace-id gic-workspace-… --initiative-id gic-initiative-… --input approval-decision.json
```

Create and publish an approved record:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 create-publication \
  --workspace-id gic-workspace-… --initiative-id gic-initiative-… --input publication.json

python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 publish \
  --publication-id gic-publication-… --publisher-id reviewer@example.org
```

Export a complete workspace bundle:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 export \
  --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
```

## Canonical contract CLI

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
[global_impact_catalyst_indicator_registry]
[global_impact_catalyst_measurement_portfolio]
[global_impact_catalyst_review_workflow]
```

The public demo is stateless. The repository interfaces require an authenticated user with `edit_posts` capability. The review workflow displays assignments and publication status and supports governed quality review operations through nonce-protected REST routes.

## JSON Schemas and examples

- `schemas/global_impact_contract.schema.json` — canonical contract v1.1.0
- `schemas/global_impact_evidence_chain.schema.json` — evidence chain v1.3.0
- `schemas/global_impact_indicator_registry.schema.json` — indicator registry v1.4.0
- `schemas/global_impact_measurement_repository.schema.json` — measurement repository v1.5.0
- `schemas/global_impact_review_workflow.schema.json` — review workflow v1.6.0
- `schemas/global_impact_workspace_bundle.schema.json` — complete workspace bundle v1.6.0
- `examples/example_global_impact_review_workflow.json`
- `examples/example_global_impact_workspace_bundle.json`

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
node --check wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-review.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

## Repository structure

```text
app/                                  Application-facing service wrapper
contracts/                            Canonical fixtures and legacy imports
data/                                 Compact authoring sample
docs/                                 Contract, evidence, registry, measurement, review, and WordPress docs
examples/                             Contract and repository examples
migrations/                           Versioned SQLite migrations
python/global_impact_core.py          Canonical v1.1.0 engine
python/global_impact_repository.py    SQLite repository and workspace bundles
python/global_impact_registry.py      Units, indicators, baselines, targets, and methods
python/global_impact_measurement.py   Observations, beneficiaries, finances, results, and portfolios
python/global_impact_review.py        Roles, review, quality, revisions, corrections, and publications
python/global_impact_service.py       Shared application service
schemas/                              Contract and repository JSON Schemas
scripts/gic_repository.py             Repository CLI
wordpress/                            Public demo and authenticated repository interfaces
```

## Governance boundary

Global Impact Catalyst improves structure, persistence, integrity signals, reproducibility, and review visibility. A quality score is a documented reviewer judgment, not an audit opinion. Approval records internal governance, not external assurance. Publication confirms that configured workflow gates were met for a specific content hash; it does not establish source truth, regulatory compliance, attribution, causal proof, certification, or impact assurance.

## License

See `LICENSE`.

## v1.7.0 analytical repository

The analysis layer adds governed time-series trends, benchmarks, comparison sets, scenario models, target-trajectory gaps, uncertainty intervals, sensitivity analysis, and persisted analytical runs. Use `python scripts/gic_repository.py --help` for the new commands or embed `[global_impact_catalyst_analysis_studio]` for the authenticated WordPress surface. Existing calculations remain governed by canonical contract v1.1.0.
