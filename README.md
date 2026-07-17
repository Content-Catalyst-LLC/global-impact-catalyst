# Global Impact Catalyst

Global Impact Catalyst is open public-interest infrastructure for defining, validating, saving, sourcing, governing, and transporting impact-measurement records. It combines a canonical impact-contract engine with persistent initiatives and portfolios, a versioned evidence chain, and a governed indicator registry for units, baselines, targets, formulas, and reusable methods.

The system is not an ESG assurance platform, certification tool, audit substitute, causal-proof engine, regulatory filing system, or automatic truth system.

## v1.4.0 — Indicator Registry, Units, Baselines, Targets, and Methods

v1.4.0 adds a reusable measurement-definition layer around the canonical v1.1.0 contract, the v1.2.0 persistent repository, and the v1.3.0 evidence chain:

- Standard and workspace-specific units with dimensions, symbols, precision, and affine conversion rules
- Unit-compatibility checks that reject conversion across incompatible dimensions
- Versioned indicator definitions with direction, unit, disaggregation, formula, and quality metadata
- A constrained formula language (`gic-expression-1.0`) that permits arithmetic without arbitrary code execution
- Versioned baseline models for point, average, rolling, benchmark, and modelled baselines
- Versioned target models for absolute, range, relative, linear, step, exponential, and custom trajectories
- Reusable method definitions with input requirements, quality profiles, limitations, and lifecycle status
- Stable bindings connecting initiative indicators to their governed definition, baseline, target, and method versions
- Automatic registry materialization when canonical contracts are saved or imported
- Schema-validated registry export and lossless workspace backup and restore
- Python service, CLI, and authenticated WordPress registry workflows

The package, application, repository schema, workspace bundle, indicator registry, and WordPress plugin are v1.4.0. The evidence-chain format remains v1.3.0 and the canonical calculation contract remains v1.1.0 because this release does not change existing metric outputs or browser/Python parity fixtures.

## Architecture

```text
compact authoring input
        ↓
canonical v1.1.0 contract + validation engine
        ↓
application service
        ↓
SQLite repository / CLI / WordPress repository
        ├── initiatives + portfolios + autosaves + audit history
        ├── sources + immutable versions + evidence + datasets + provenance
        └── units + indicator definitions + baselines + targets + methods
                                      ↓
                  versioned indicator registry bindings
                                      ↓
 workspace bundle / evidence export / registry export / backup and restore
```

Canonical contracts remain complete JSON snapshots. Evidence and registry records are additive governed repository objects. Updating a unit, indicator definition, baseline, target, or method creates a new version rather than rewriting the version already bound to a saved initiative.

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

Saving materializes the contract’s source and provenance records and binds its indicator to governed indicator, baseline, target, and method definitions.

List standard and custom units:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  units
```

Register a custom unit:

```bash
python3 scripts/gic_repository.py \
  --database outputs/global-impact-catalyst.sqlite3 \
  add-unit \
  --workspace-id gic-workspace-… \
  --input unit.json
```

Register an indicator definition and its measurement models:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-indicator --workspace-id gic-workspace-… --input indicator.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-baseline --workspace-id gic-workspace-… --input baseline.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-target --workspace-id gic-workspace-… --input target.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 add-method --workspace-id gic-workspace-… --input method.json
```

Compute a baseline and evaluate a target trajectory:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 compute-baseline --baseline-model-id gic-baseline-model-… --observations observations.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 evaluate-target --target-model-id gic-target-model-… --baseline-value 100 --progress-fraction 0.5
```

Export the indicator registry or a complete workspace bundle:

```bash
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 indicator-registry --workspace-id gic-workspace-… --output outputs/indicator-registry.json
python3 scripts/gic_repository.py --database outputs/global-impact-catalyst.sqlite3 export --workspace-id gic-workspace-… --output outputs/workspace-bundle.json
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
[global_impact_catalyst_indicator_registry]
```

The public demo is stateless. The workspace, evidence ledger, and indicator registry require an authenticated user with `edit_posts` capability. The registry interface can inspect standard and custom units, register indicator definitions, create baseline and target models, define methods, and export a workspace registry.

## JSON Schemas and examples

- `schemas/global_impact_contract.schema.json` — canonical v1.1.0 contract
- `schemas/global_impact_evidence_chain.schema.json` — evidence-chain v1.3.0
- `schemas/global_impact_indicator_registry.schema.json` — indicator registry v1.4.0
- `schemas/global_impact_workspace_bundle.schema.json` — complete workspace bundle v1.4.0
- `examples/example_global_impact_indicator_registry.json`
- `examples/example_global_impact_workspace_bundle.json`

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
node --check wordpress/global-impact-catalyst-demo/assets/global-impact-catalyst-registry.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

## Repository structure

```text
app/                                  Application-facing service wrapper
contracts/                            Canonical fixtures and legacy import records
data/                                 Compact authoring sample
docs/                                 Contract, repository, evidence, registry, migration, and WordPress docs
examples/                             Contract, evidence, registry, and workspace examples
migrations/                           Versioned SQLite migration inventory
python/global_impact_core.py          Canonical v1.1.0 engine
python/global_impact_repository.py    SQLite repository and evidence chain
python/global_impact_registry.py      Units, indicator definitions, baselines, targets, and methods
python/global_impact_service.py       Shared application service
schemas/                              Contract, evidence, registry, and workspace schemas
scripts/gic_repository.py             Repository, evidence, and registry CLI
tests/                                Engine, parity, repository, evidence, registry, and integration tests
wordpress/                            Demo, workspace, evidence-ledger, and registry plugin
```

## Methodological boundary

Global Impact Catalyst improves structure, persistence, integrity signals, reproducibility, and review visibility. A unit conversion demonstrates numerical compatibility under registered rules; it does not establish methodological comparability. A formula result is a derived value under declared inputs; it is not causal proof. A baseline or target trajectory is a governed model, not an assurance opinion. Human review remains required for interpretation, publication, and stronger claims.

## License

See `LICENSE`.
