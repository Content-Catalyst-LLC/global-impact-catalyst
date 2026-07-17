# Repository Architecture — v1.4.0

```text
compact input or legacy record
        ├── Python normalizer / validator / contract builder
        └── JavaScript normalizer / validator / contract builder
                         ↓
              exact golden fixtures
                         ↓
       canonical v1.1.0 contract + validation schemas
                         ↓
                 application service
                         ↓
             SQLite / CLI / WordPress
        ├── persistence and portfolios
        ├── evidence and provenance
        └── indicator registry and immutable versions
                         ↓
 evidence export / registry export / workspace bundle / backup
```

The Python and browser contract implementations share documented algorithms and complete expected outputs rather than importing one runtime into the other. Deterministic IDs and issue IDs make exact parity observable.

- `python/global_impact_core.py`: normalization, identity, metrics, validation, contract assembly, migration, Markdown, CLI
- `python/global_impact_repository.py`: migrations, persistence, evidence, bundles, backup, and repository lifecycle
- `python/global_impact_registry.py`: units, conversions, safe formulas, indicator definitions, baseline and target models, methods, bindings, and registry restore
- `schemas/`: compact authoring, canonical contract, evidence, registry, workspace, and validation schemas
- `contracts/fixtures/`: exact runtime parity suite
- `contracts/legacy/`: migration source fixture
- `scripts/check_contracts.py`: repository and release invariants
- `scripts/check_browser_parity.js`: exact JavaScript parity
- `scripts/check_wordpress_instances.php`: rendered shortcode and route integrity
- `scripts/smoke_test.py`: portable end-to-end release check
