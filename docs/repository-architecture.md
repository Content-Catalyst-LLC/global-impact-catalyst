# Repository Architecture — v1.1.0

```text
compact input or legacy record
        ├── Python normalizer / validator / contract builder
        └── JavaScript normalizer / validator / contract builder
                         ↓
              exact golden fixtures
                         ↓
       canonical contract + validation schemas
                         ↓
 JSON / Markdown / WordPress presentation / migration
```

The two implementations share documented algorithms and complete expected outputs rather than importing one runtime into the other. Deterministic IDs and issue IDs make exact parity observable.

- `python/global_impact_core.py`: normalization, identity, metrics, validation, contract assembly, migration, Markdown, CLI
- `schemas/`: compact authoring, canonical contract, compatibility, and validation-result schemas
- `contracts/fixtures/`: exact runtime parity suite
- `contracts/legacy/`: migration source fixture
- `scripts/check_contracts.py`: repository and release invariants
- `scripts/check_browser_parity.js`: exact JavaScript parity
- `scripts/check_wordpress_instances.php`: rendered shortcode integrity
- `scripts/smoke_test.py`: portable end-to-end release check
