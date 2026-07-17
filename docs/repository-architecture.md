# Repository Architecture — v1.5.0

```text
compact input or legacy record
        ├── Python canonical engine
        └── JavaScript canonical engine
                         ↓
              exact golden fixtures
                         ↓
       canonical v1.1.0 contract + validation
                         ↓
                 application service
                         ↓
             SQLite / CLI / WordPress
        ├── initiatives, autosaves, audit, bundles
        ├── sources, versions, evidence, provenance
        ├── units, indicators, baselines, targets, methods
        └── results, observations, beneficiaries, finances, portfolios
                         ↓
 evidence / registry / measurement exports / workspace bundle / backup
```

- `python/global_impact_core.py`: normalization, identity, metrics, validation, migration, Markdown, CLI
- `python/global_impact_repository.py`: migrations, persistent entities, workspace bundles, backup, and restore
- `python/global_impact_registry.py`: units, safe formulas, indicator definitions, baseline and target models, methods, and bindings
- `python/global_impact_measurement.py`: multi-period observations, aggregate beneficiary records, financial records, impact results, contribution context, and guarded portfolios
- `schemas/`: canonical, evidence, registry, measurement, and workspace schemas
- `contracts/fixtures/`: exact Python/browser parity suite
- `scripts/check_contracts.py`: release invariants
- `scripts/smoke_test.py`: portable end-to-end lifecycle validation
